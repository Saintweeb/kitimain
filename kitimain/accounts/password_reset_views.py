"""
accounts/password_reset_views.py
Email-based password reset using Django's built-in tokens.
"""
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

User = get_user_model()


class RequestPasswordResetView(APIView):
    """
    POST /api/auth/password-reset/
    Body: { "email": "alice@kiti.ac.ke" }
    Sends a reset link to the user's email.
    Always returns 200 so we don't leak whether an email exists.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'detail': 'Email is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether user exists
            return Response({'detail': 'If that email exists, a reset link has been sent.'})

        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{settings.FRONTEND_URL}/reset-password.html?uid={uid}&token={token}"

        # Render email
        subject = 'KITI ICT – Password Reset Request'
        message = f"""Hello {user.full_name},

You requested a password reset for your KITI ICT Department account.

Click the link below to set a new password (valid for 1 hour):

{reset_url}

If you did not request this, please ignore this email.

– KITI ICT Department
"""
        html_message = f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#0a0d14;color:#e8eaf0;padding:32px;border-radius:12px">
  <h1 style="color:#00f5d4;font-size:24px;margin-bottom:8px">KITI ICT Department</h1>
  <p style="color:#6b7280;margin-bottom:24px">Password Reset Request</p>
  <p>Hello <strong>{user.full_name}</strong>,</p>
  <p>You requested a password reset. Click the button below — the link is valid for <strong>1 hour</strong>.</p>
  <div style="text-align:center;margin:32px 0">
    <a href="{reset_url}"
       style="background:linear-gradient(135deg,#7c3aed,#00f5d4);color:#fff;padding:14px 32px;
              border-radius:10px;text-decoration:none;font-weight:700;font-size:16px">
      Reset My Password
    </a>
  </div>
  <p style="font-size:12px;color:#6b7280">If the button doesn't work, copy this link:<br>
    <a href="{reset_url}" style="color:#00f5d4">{reset_url}</a>
  </p>
  <hr style="border-color:#1e2640;margin:24px 0">
  <p style="font-size:12px;color:#6b7280">If you did not request this, ignore this email.</p>
</div>
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return Response({'detail': 'If that email exists, a reset link has been sent.'})


class ConfirmPasswordResetView(APIView):
    """
    POST /api/auth/password-reset/confirm/
    Body: { "uid": "...", "token": "...", "new_password": "..." }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid          = request.data.get('uid', '')
        token        = request.data.get('token', '')
        new_password = request.data.get('new_password', '')

        if not all([uid, token, new_password]):
            return Response(
                {'detail': 'uid, token and new_password are required.'},
                status=400
            )

        if len(new_password) < 8:
            return Response(
                {'detail': 'Password must be at least 8 characters.'},
                status=400
            )

        try:
            pk   = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Invalid reset link.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Reset link is invalid or has expired.'},
                status=400
            )

        user.set_password(new_password)
        user.save()

        return Response({'detail': 'Password reset successful. You can now log in.'})


class ValidateResetTokenView(APIView):
    """
    GET /api/auth/password-reset/validate/?uid=...&token=...
    Frontend calls this to check if link is still valid before showing the form.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        uid   = request.query_params.get('uid', '')
        token = request.query_params.get('token', '')

        try:
            pk   = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'valid': False, 'detail': 'Invalid link.'})

        if default_token_generator.check_token(user, token):
            return Response({'valid': True, 'full_name': user.full_name})

        return Response({'valid': False, 'detail': 'Link expired.'})
