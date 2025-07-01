import requests
from datetime import date
from .models import ExchangeRate
from django.conf import settings


class FrankfurterService:
    BASE_URL = settings.FRANKFURTER_API_URL

    def get_historical_rates(self, base, symbols, start_date, end_date):
        url = f"{self.BASE_URL}/{start_date}..{end_date}"
        params = {"base": base, "symbols": ",".join(symbols)}

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
