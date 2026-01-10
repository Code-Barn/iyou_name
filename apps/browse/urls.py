from django.urls import path

from .views import browse_individuals, individual_detail, select_individual

app_name = "browse"

urlpatterns = [
    path("", browse_individuals, name="browse_individuals"),
    path("select/", select_individual, name="select_individual"),
    path("person/<str:ind_id>/", individual_detail, name="individual_detail"),
]
