from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Currency, ExchangeRate
from .services import FrankfurterAPIService
from datetime import date, timedelta
from django import forms
from django.http import JsonResponse
from django.conf import settings
import pandas as pd


class ExchangeRateForm(forms.Form):
    base_currency_code = forms.ChoiceField(
        choices=[(code, code) for code in settings.SUPPORTED_CURRENCIES]
    )
    target_currency_code = forms.ChoiceField(
        choices=[(code, code) for code in settings.SUPPORTED_CURRENCIES]
    )
    days = forms.IntegerField(required=True, min_value=1, max_value=365 * 2)


@require_http_methods(["GET"])
def exchange_rate(request):
    form = ExchangeRateForm(request.GET)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    base_currency = Currency.objects.get(code=form.cleaned_data["base_currency_code"])
    target_currency = Currency.objects.get(
        code=form.cleaned_data["target_currency_code"]
    )
    days = form.cleaned_data.get("days") - 1
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

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
            "base_currency": rates[0].base_currency.to_dict(),
            "target_currency": rates[0].target_currency.to_dict(),
            "rates": [{"rate": r.rate, "date": r.date} for r in rates],
        }
    )


@require_http_methods(["GET"])
def available_currencies(request):
    # if we dont have any in database, get from API first.
    # # This is technically only for debugging, as we would assume that the data would be pre-populated and never be empty
    if Currency.objects.count() != len(settings.SUPPORTED_CURRENCIES):
        available_currencies = FrankfurterAPIService().get_available_currencies()
        Currency.objects.bulk_create(available_currencies, ignore_conflicts=True)

    return JsonResponse({"data": [c.to_dict() for c in Currency.objects.all()]})
