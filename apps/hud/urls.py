from django.urls import path

from .views import generate_tree_chart
from .views_simple_buffered import (
    display_tree_hud,
    get_template_preview_simple,
    save_hud_settings,
    apply_settings_change,
    get_buffer_stats,
    update_settings_timestamp,
    get_settings_panel,
    get_file_individuals,
)
from .test_views import (
    test_enhanced_1gen_preview,
    test_enhanced_1gen_comparison,
)

app_name = "hud"

urlpatterns = [
    path(
        "generate-chart/<int:document_id>/",
        generate_tree_chart,
        name="generate_tree_chart",
    ),
    path("display-tree/", display_tree_hud, name="display_tree"),
    path("save-settings/", save_hud_settings, name="save_settings"),
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
        "update-settings-timestamp/",
        update_settings_timestamp,
        name="update_settings_timestamp",
    ),
    path(
        "get-file-individuals/",
        get_file_individuals,
        name="get_file_individuals",
    ),
    # Test endpoints
    path(
        "test-enhanced-1gen-preview/",
        test_enhanced_1gen_preview,
        name="test_enhanced_1gen_preview",
    ),
    path(
        "test-enhanced-1gen-comparison/",
        test_enhanced_1gen_comparison,
        name="test_enhanced_1gen_comparison",
    ),
]
