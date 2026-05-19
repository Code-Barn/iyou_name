from django.urls import path

from .views import (
    delete_gedcom_file,
    get_shared_with_users,
    profile,
    remove_gedcom_share,
    share_gedcom_file,
    sync_gedcom_file,
)
from .did_views import (
    add_vc,
    generate_did,
    get_did,
    get_vcs_by_type,
    issue_vc,
    list_vcs,
    verify_vc,
)

app_name = "users"

urlpatterns = [
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
    path("api/did/generate/", generate_did, name="generate_did"),
    path("api/did/", get_did, name="get_did"),
    path("api/did/verify/", verify_vc, name="verify_vc"),
    path("api/did/vc/add/", add_vc, name="add_vc"),
    path("api/did/vcs/", list_vcs, name="list_vcs"),
    path("api/did/vcs/type/<str:vc_type>/", get_vcs_by_type, name="get_vcs_by_type"),
    path("api/did/vc/issue/", issue_vc, name="issue_vc"),
]
