from django.urls import path
from .views import adjust_output, generate_chart

app_name = "charts"

urlpatterns = [
    path("tune/", adjust_output, name="adjust_output"),
    path("generate/", generate_chart, name="generate_chart"),
]
