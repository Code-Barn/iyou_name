from django.urls import path

from .views import generate_chart

app_name = "charts"

urlpatterns = [
    path("generate/", generate_chart, name="generate_chart"),
]
