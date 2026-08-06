from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    question_create,
    question_detail,
    question_list,
    success_story_create,
    success_story_detail,
    success_story_list,
    profile_edit,
)

from . import views

urlpatterns = [
    # --- Scholarships ---
    path("", views.scholarship_list, name="scholarship-list"),
    path("scholarship/<slug:slug>/", views.scholarship_detail, name="scholarship-detail"),
    path("scholarship/<slug:slug>/toggle-save/", views.toggle_save_scholarship, name="toggle-save-scholarship"),
    path("profile/", views.profile_view, name="profile"),

    # --- Authentication ---
    # Login and logout are Django's built-in views — no custom logic needed,
    # just point them at our own templates so they match the site's design.
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="scholarship-list"),
        name="logout",
    ),
    # Signup needs custom logic (create account + log in), so it's our own
    # function-based view from views.py.
    path("accounts/signup/", views.signup_view, name="signup"),

    # --- Password reset (uses Django's built-in email-based flow) ---
    path(
        "accounts/password-reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "accounts/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
        path("profile/edit/", profile_edit, name="profile-edit"),
 
    path("stories/", success_story_list, name="story-list"),
    path("stories/new/", success_story_create, name="story-create"),
    path("stories/<int:pk>/", success_story_detail, name="story-detail"),
 
    path("questions/", question_list, name="question-list"),
    path("questions/new/", question_create, name="question-create"),
    path("questions/<int:pk>/", question_detail, name="question-detail"),
 
    # --- Password reset (for regular site users -- NOT the /admin/ one) ---
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notification-read"),
    path("notifications/mark-all-read/", views.mark_all_notifications_read, name="notifications-mark-all-read"),

]


