from django.urls import path
from .views import display_tree_hud, save_hud_settings, get_hud_family_data, get_hud_preview, get_hud_settings

app_name = "hud"

urlpatterns = [
    path("display-tree/", display_tree_hud, name="display_tree"),
    path("save-settings/", save_hud_settings, name="save_settings"),
    path("api/family-data/", get_hud_family_data, name="hud_family_data"),
    path("api/preview/", get_hud_preview, name="hud_preview"),
    path("api/settings/", get_hud_settings, name="hud_settings"),
]
