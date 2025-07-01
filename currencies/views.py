from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Currency, ExchangeRate
from .services import FrankfurterAPIService
from datetime import date, timedelta
from django import forms
from django.http import JsonResponse


class ExchangeRateForm(forms.Form):
    base_currency_code = forms.CharField(max_length=3, required=True)
    target_currency_code = forms.CharField(max_length=3, required=True)
    days = forms.IntegerField(required=False, min_value=1, max_value=365)


@require_http_methods(["GET"])
def exchange_rate(request):
    form = ExchangeRateForm(request.GET)

    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    base_currency_code = form.cleaned_data["base_currency_code"]
    target_currency_code = form.cleaned_data["target_currency_code"]
    days = form.cleaned_data.get("days") or 0

    rates = FrankfurterAPIService().get_historical_rates(
        base_currency_code,
        target_currency_code,
        date.today() - timedelta(days=days),
        date.today(),
    )

    return JsonResponse({"data": [r.to_dict() for r in rates]})


@require_http_methods(["GET"])
def available_currencies(request):
    # if we dont have any in database, get from API first.
    # # This is technically only for debugging, as we would assume that the data would be pre-populated and never be empty
    if Currency.objects.count() == 0:
        available_currencies = FrankfurterAPIService().get_available_currencies()
        Currency.objects.bulk_create(available_currencies)

    return JsonResponse({"data": [c.to_dict() for c in Currency.objects.all()]})
