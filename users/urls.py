from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import link_telegram, telegram_callback

urlpatterns = [
    # Аутентификация
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('accounts/set-password/', views.set_password_view, name='set_password'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_view, name='profile'),


    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="emails/password_reset_email.html"
        ),
        name="password_reset"
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_form.html"
        ),
        name="password_reset_confirm"
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),

    path('api/telegram/link/', link_telegram),
    path('telegram/callback/', telegram_callback, name='telegram_callback'),
]
