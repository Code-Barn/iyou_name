from django.urls import path

from .views import generate_final_chart, test_pdf_generation, test_template_selection

app_name = "generator"

urlpatterns = [
    path("generate/", generate_final_chart, name="generate_final_chart"),
    path("test-template/", test_template_selection, name="test_template_selection"),
    path("test-pdf/", test_pdf_generation, name="test_pdf_generation"),
]
