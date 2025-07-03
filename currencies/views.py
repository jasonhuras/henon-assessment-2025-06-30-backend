from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from currencies.utils import currency_utils
from .models import Currency, ExchangeRate
from .services import FrankfurterAPIService
from .forms import ExchangeRateForm
from datetime import date, timedelta
import pandas as pd


@require_http_methods(["GET", "OPTIONS"])
def exchange_rate(request):
    form = ExchangeRateForm(request.GET)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    base_currency = Currency.objects.get(code=form.cleaned_data["base_currency_code"])
    target_currency = Currency.objects.get(
        code=form.cleaned_data["target_currency_code"]
    )
    start_date = form.cleaned_data["start_date"]
    end_date = form.cleaned_data["end_date"]

    # checking what we have in Database...
    existing_dates = set(
        ExchangeRate.objects.filter(
            base_currency=base_currency,
            target_currency=target_currency,
            date__range=(start_date, end_date),
        ).values_list("date", flat=True)
    )

    # filtering out non-business days, as they are excluded in frankfurter api
    business_days = pd.bdate_range(start=start_date, end=end_date)
    required_dates = set(business_days.date)

    # calculating difference between request and database Rows
    missing_dates = required_dates - existing_dates

    if missing_dates:
        # if dates are missing, we first get from frankfurter, and persist to database
        missing_rates = FrankfurterAPIService().get_historical_rates(
            base_currency, target_currency, min(missing_dates), max(missing_dates)
        )
        print(f"dates missing, getting {len(missing_rates)} rates from api")
        ExchangeRate.objects.bulk_create(missing_rates, ignore_conflicts=True)

    rates = ExchangeRate.objects.filter(
        base_currency=base_currency,
        target_currency=target_currency,
        date__range=(start_date, end_date),
    ).order_by("date")

    if not rates:
        return JsonResponse({"rates": []})

    return JsonResponse(
        {
            "data": {
                "code": f"{base_currency.code}{target_currency.code}",
                "rates": [{"rate": r.rate, "date": r.date} for r in rates],
            }
        }
    )


@require_http_methods(["GET", "OPTIONS"])
def supported_currencies(request):
    # if we dont have any in database, get from API first.
    # # This is technically only for debugging, as we would assume that the data would be pre-populated and never be empty
    if Currency.objects.count() != len(settings.SUPPORTED_CURRENCIES):
        available_currencies = FrankfurterAPIService().get_available_currencies()
        Currency.objects.bulk_create(available_currencies, ignore_conflicts=True)

    return JsonResponse(
        {"data": currency_utils.format_currency_pairs(Currency.objects.all())}
    )


# this would not be exposed to all users, ideally this would be locked down with an authentication key/role
# ideally this would be called by scheduling done through infrastructure, like a lambda or cron job to handle errors and work in distributed/scaled env
@require_http_methods(["POST", "OPTIONS"])
def load_monthly_data(request):

    last_day_of_last_month = date.today().replace(day=1) - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)

    currencies = Currency.objects.all()

    # generating all combinations
    # we dont use the util method here because we need to access the actual Currency object
    for base_currency in currencies:
        for target_currency in currencies:

            # skip CAD/CAD for example
            if base_currency == target_currency:
                continue

            exchange_rates = FrankfurterAPIService().get_historical_rates(
                base_currency,
                target_currency,
                first_day_of_last_month,
                last_day_of_last_month,
            )

            print(
                f"loading data for {base_currency.code}/{target_currency.code} of size {len(exchange_rates)}"
            )

            ExchangeRate.objects.bulk_create(exchange_rates, ignore_conflicts=True)

    return HttpResponse(status=204)
