from django.urls import path
from .views import browse_individuals, select_individual, individual_detail

app_name = "browse"

urlpatterns = [
    path("browse/", browse_individuals, name="browse_individuals"),
    path("select/", select_individual, name="select_individual"),
    path("person/<str:ind_id>/", individual_detail, name="individual_detail"),
]
