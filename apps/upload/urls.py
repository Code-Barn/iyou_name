from django.urls import path
from .views import upload_file, upload_and_generate, select_gedcom_file, delete_gedcom_file

app_name = "upload"

urlpatterns = [
    path("", upload_and_generate, name="home"),
    path("upload-file/", upload_file, name="upload_file"),
    path("select-file/<int:file_id>/", select_gedcom_file, name="select_gedcom_file"),
    path("delete-file/<int:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
]
