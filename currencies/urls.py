from django.urls import path
from . import views

urlpatterns = [
    path("rates", views.exchange_rate, name="exchange_rate"),
    path("currencies", views.available_currencies, name="available_currencies"),
    path("load-monthly-data", views.load_monthly_data, name="load_monthly_data"),
]
