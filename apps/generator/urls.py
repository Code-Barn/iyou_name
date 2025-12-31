from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    adjust_output,
    browse_individuals,
    delete_gedcom_file,
    display_tree_hud,
    generate_chart,
    get_hud_family_data,
    get_hud_preview,
    get_hud_settings,
    individual_detail,
    profile,
    register,
    save_hud_settings,
    select_gedcom_file,
    select_individual,
    upload_and_generate,
    upload_file,
)

app_name = "generator"

urlpatterns = [
    path("", upload_and_generate, name="home"),
    path("upload-file/", upload_file, name="upload_file"),
    path("select/", select_individual, name="select_individual"),
    path("browse/", browse_individuals, name="browse_individuals"),
    path("person/<str:ind_id>/", individual_detail, name="individual_detail"),
    path("tune/", adjust_output, name="adjust_output"),
    path("generate/", generate_chart, name="generate_chart"),
    # HUD Display and Settings
    path("display-tree/", display_tree_hud, name="display_tree"),
    path("save-settings/", save_hud_settings, name="save_settings"),
    # HUD API endpoints
    path("api/family-data/", get_hud_family_data, name="hud_family_data"),
    path("api/preview/", get_hud_preview, name="hud_preview"),
    path("api/settings/", get_hud_settings, name="hud_settings"),
    # User Profile Paths
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
    path("select-file/<int:file_id>/", select_gedcom_file, name="select_gedcom_file"),
    path("delete-file/<int:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="generator/login.html", next_page="generator:home"
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="generator/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="generator/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="generator/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="generator/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="generator/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="generator/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
