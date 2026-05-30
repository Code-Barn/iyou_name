from django.urls import path
from django.views.generic.base import RedirectView

from .views import (
    delete_gedcom_file,
    get_shared_with_users,
    profile,
    remove_gedcom_share,
    share_gedcom_file,
    sync_gedcom_file,
)

app_name = "users"

urlpatterns = [
    path("login/", RedirectView.as_view(pattern_name="oidc_authentication_init"), name="login"),
    path("register/", RedirectView.as_view(pattern_name="oidc_authentication_init"), name="register"),
    path("logout/", RedirectView.as_view(pattern_name="oidc_logout"), name="logout"),
    path("profile/", profile, name="profile"),
    path("delete-file/<int:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
    path("sync-file/<int:file_id>/", sync_gedcom_file, name="sync_gedcom_file"),
    path("share-file/<int:file_id>/", share_gedcom_file, name="share_gedcom_file"),
    path(
        "remove-share/<int:file_id>/<int:user_id>/",
        remove_gedcom_share,
        name="remove_gedcom_share",
    ),
    path(
        "shared-with/<int:file_id>/",
        get_shared_with_users,
        name="get_shared_with_users",
    ),
]
