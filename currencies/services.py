import requests
from datetime import date, datetime
from .models import ExchangeRate, Currency
from django.conf import settings


class FrankfurterAPIService:
    BASE_URL = settings.FRANKFURTER_API_URL

    def get_historical_rates(
        self, base: str, target: str, start_date: date, end_date: date
    ) -> list[ExchangeRate]:
        url = f"{self.BASE_URL}/{start_date}..{end_date}"
        params = {"base": base, "symbols": target}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        exchange_rates = []

        for date_str, currency_rate in data["rates"].items():
            for target_currency, rate in currency_rate.items():
                exchange_rate = ExchangeRate(
                    base_currency=Currency.objects.get(code=data["base"]),
                    target_currency=Currency.objects.get(code=target_currency),
                    rate=rate,
                    date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                )
                exchange_rates.append(exchange_rate)

        return exchange_rates

    def get_available_currencies(self) -> list[Currency]:
        url = f"{self.BASE_URL}/currencies"

        response = requests.get(url)
        response.raise_for_status()

        currencies = [
            Currency(code=code, name=name) for code, name in response.json().items()
        ]

        return currencies
