from django.urls import path
from . import views

urlpatterns = [
    path("rates/", views.exchange_rate, name="exchange_rate"),
]
