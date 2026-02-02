from django.urls import path

from .views import (
    display_tree_hud,
    get_1gen_preview,
    get_hud_family_data,
    get_hud_preview,
    get_hud_settings,
    get_template_preview,
    save_hud_settings,
    update_settings_timestamp,
)

app_name = "hud"

urlpatterns = [
    path("display-tree/", display_tree_hud, name="display_tree"),
    path("save-settings/", save_hud_settings, name="save_settings"),
    path("get-family-data/", get_hud_family_data, name="get_family_data"),
    path("get-preview/", get_hud_preview, name="get_preview"),
    path("get-settings/", get_hud_settings, name="get_settings"),
    path("get-1gen-preview/", get_1gen_preview, name="get_1gen_preview"),
    path(
        "get-template-preview/<str:template_id>/",
        get_template_preview,
        name="get_template_preview",
    ),
    path(
        "update-settings-timestamp/",
        update_settings_timestamp,
        name="update_settings_timestamp",
    ),
]
