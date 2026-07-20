from django.urls import path

from .views import generate_chart

app_name = "charts"

urlpatterns = [
    path(
        "generate/<int:file_id>/<str:individual_id>/",
        generate_chart,
        name="generate_chart",
    ),
]
