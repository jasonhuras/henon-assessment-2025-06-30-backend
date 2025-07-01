import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    days = forms.IntegerField(required=False, min_value=1, max_value=365)


@require_http_methods(["GET"])
def exchange_rate(request):
    form = ExchangeRateForm(request.GET)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    base_currency = Currency.objects.get(code=form.cleaned_data["base_currency_code"])
    target_currency = Currency.objects.get(
        code=form.cleaned_data["target_currency_code"]
    )
    days = form.cleaned_data.get("days") or 0
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
    business_days = pd.bdate_range(start=start_date, end=end_date)
    required_dates = set(business_days.date)
    # calculating difference between request and database Rows
    missing_dates = required_dates - existing_dates

    if missing_dates:
        print(missing_dates)
        print("dates missing, getting from api")
        missing_rates = FrankfurterAPIService().get_historical_rates(
            base_currency, target_currency, min(missing_dates), max(missing_dates)
        )
        print([a.date for a in missing_rates])
        # Filter to only missing dates to avoid duplicates, this is in case we have existing rates in the range of missing rates
        new_rates = [rate for rate in missing_rates if rate.date in missing_dates]
        ExchangeRate.objects.bulk_create(new_rates, ignore_conflicts=True)

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
    if Currency.objects.count() == 0:
        available_currencies = FrankfurterAPIService().get_available_currencies()
        Currency.objects.bulk_create(available_currencies)

    return JsonResponse({"data": [c.to_dict() for c in Currency.objects.all()]})
