from django.urls import path

from apps.chart_storage.preset_views import (
    list_presets,
    create_preset,
    get_preset,
    update_preset,
    delete_preset,
    set_default_preset,
)
from apps.chart_storage.individual_settings_views import (
    list_individual_settings,
    save_individual_settings,
    get_individual_settings,
    delete_individual_settings,
    set_home_person,
    get_home_person,
)
from apps.chart_storage.photo_views import (
    get_photo,
    upload_photo,
    delete_photo,
)
from apps.chart_storage.storage_views import (
    get_storage_usage,
    clear_all_buffers,
    get_buffer_list,
)

app_name = "chart_storage"

urlpatterns = [
    # Presets
    path("presets/", list_presets, name="list_presets"),
    path("presets/create/", create_preset, name="create_preset"),
    path("presets/<int:preset_id>/", get_preset, name="get_preset"),
    path("presets/<int:preset_id>/update/", update_preset, name="update_preset"),
    path("presets/<int:preset_id>/delete/", delete_preset, name="delete_preset"),
    path(
        "presets/<int:preset_id>/set-default/",
        set_default_preset,
        name="set_default_preset",
    ),
    # Individual Settings
    path(
        "individual-settings/",
        list_individual_settings,
        name="list_individual_settings",
    ),
    path(
        "individual-settings/save/",
        save_individual_settings,
        name="save_individual_settings",
    ),
    path(
        "individual-settings/<str:gedcom_hash>/<str:individual_id>/",
        get_individual_settings,
        name="get_individual_settings",
    ),
    path(
        "individual-settings/<str:gedcom_hash>/<str:individual_id>/delete/",
        delete_individual_settings,
        name="delete_individual_settings",
    ),
    path("home-person/set/", set_home_person, name="set_home_person"),
    path("home-person/<str:gedcom_hash>/", get_home_person, name="get_home_person"),
    # Storage
    path("storage/usage/", get_storage_usage, name="get_storage_usage"),
    path("storage/clear/", clear_all_buffers, name="clear_all_buffers"),
    path("storage/buffers/", get_buffer_list, name="get_buffer_list"),
    # Individual Photos
    path("photos/upload/", upload_photo, name="upload_photo"),
    path(
        "photos/<str:gedcom_hash>/<str:individual_id>/",
        get_photo,
        name="get_photo",
    ),
    path(
        "photos/<str:gedcom_hash>/<str:individual_id>/delete/",
        delete_photo,
        name="delete_photo",
    ),
]
