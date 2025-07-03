from django.urls import path
from . import views

urlpatterns = [
    path("exchange-rates/", views.exchange_rate, name="exchange_rate"),
    path(
        "supported-currencies/", views.supported_currencies, name="supported-currencies"
    ),
    path("load-monthly-data/", views.load_monthly_data, name="load_monthly_data"),
]
