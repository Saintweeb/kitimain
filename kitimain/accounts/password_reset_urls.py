"""accounts/password_reset_urls.py"""
from django.urls import path
from .password_reset_views import (
    RequestPasswordResetView,
    ConfirmPasswordResetView,
    ValidateResetTokenView,
)

urlpatterns = [
    path('password-reset/',          RequestPasswordResetView.as_view(),  name='password-reset-request'),
    path('password-reset/confirm/',  ConfirmPasswordResetView.as_view(),  name='password-reset-confirm'),
    path('password-reset/validate/', ValidateResetTokenView.as_view(),    name='password-reset-validate'),
]
