from django.contrib.auth import views as auth_views
from django.urls import path

from .views import delete_gedcom_file, profile, register, user_login

app_name = "users"

urlpatterns = [
    path("auth/register/", register, name="register"),
    path("profile/", profile, name="profile"),
    path("auth/login/", user_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("delete-file/<int:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
    path(
        "auth/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="users/auth/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "auth/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="users/auth/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "auth/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/auth/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "auth/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
