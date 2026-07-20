from django.urls import path

from .views import confirm_selection, select_individual

app_name = "selector"

urlpatterns = [
    path("select/<int:file_id>/", select_individual, name="select_individual"),
    path("confirm/<int:file_id>/", confirm_selection, name="confirm_selection"),
]
