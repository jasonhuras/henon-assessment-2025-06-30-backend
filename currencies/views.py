from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Currency, ExchangeRate
from .services import FrankfurterService
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

    return JsonResponse(
        {
            "data": FrankfurterService().get_historical_rates(
                base_currency_code,
                [target_currency_code],
                date.today() - timedelta(days=days),
                date.today(),
            )
        }
    )
