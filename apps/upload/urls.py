from django.urls import path

from .views import (
    delete_gedcom_file,
    select_gedcom_file,
    set_current_gedcom_file,
    upload_and_generate,
    upload_file,
)

app_name = "upload"

urlpatterns = [
    path("", upload_and_generate, name="home"),
    path("upload-file/", upload_file, name="upload_file"),
    path("select-file/<int:file_id>/", select_gedcom_file, name="select_gedcom_file"),
    path("delete-file/<int:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
    path(
        "set-current-file/<int:file_id>/",
        set_current_gedcom_file,
        name="set_current_gedcom_file",
    ),
]
