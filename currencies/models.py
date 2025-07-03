from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # like CAD or EUR etc.
    name = models.CharField(max_length=100)  # like Canadian Dollar etc.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "currency"


class ExchangeRate(models.Model):
    base_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="base_rates"
    )  # numerator, like EUR/USD -> EUR
    target_currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="target_rates"
    )  # denominator, like EUR/USD -> USD
    rate = models.DecimalField(max_digits=15, decimal_places=6)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["base_currency", "target_currency", "date"]
        db_table = "exchange_rate"
