from django.urls import path

from .views_simple_buffered import (
    display_tree_hud,
    get_template_preview_simple,
    save_hud_settings,
    apply_settings_change,
    get_buffer_stats,
)
from .views import (
    get_1gen_preview,
    get_hud_family_data,
    get_settings_panel,
    update_settings_timestamp,
    get_file_individuals,
)

app_name = "hud"

urlpatterns = [
    path("display-tree/", display_tree_hud, name="display_tree"),
    path("save-settings/", save_hud_settings, name="save_settings"),
    path("get-family-data/", get_hud_family_data, name="get_family_data"),
    path("get-preview/", get_1gen_preview, name="get_preview"),
    path("get-1gen-preview/", get_1gen_preview, name="get_1gen_preview"),
    path(
        "get-template-preview/<str:template_id>/",
        get_template_preview_simple,
        name="get_template_preview",
    ),
    path(
        "apply-settings-change/",
        apply_settings_change,
        name="apply_settings_change",
    ),
    path(
        "get-buffer-stats/",
        get_buffer_stats,
        name="get_buffer_stats",
    ),
    path(
        "get-settings-panel/<str:template_name>/",
        get_settings_panel,
        name="get_settings_panel",
    ),
    path(
        "apply-settings-change/",
        apply_settings_change,
        name="apply_settings_change",
    ),
    path(
        "update-settings-timestamp/",
        update_settings_timestamp,
        name="update_settings_timestamp",
    ),
    path(
        "get-file-individuals/",
        get_file_individuals,
        name="get_file_individuals",
    ),
]
