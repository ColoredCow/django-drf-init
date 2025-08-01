import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.responses import error_response, success_response
from apps.user.emails.reset_email import send_password_reset_email
from apps.user.permissions.groups import IsAdmin

from .models import CustomUser
from .serializers import CustomUserSerializer, LoginSerializer, RegistrationSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ["retrieve"]:
            return [IsAdmin]
        return False


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "email": user.email, "full_name": user.full_name},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_data = {
            "tokens": {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            },
            "user": {
                "email": serializer.validated_data["email"],
                "full_name": serializer.validated_data["full_name"],
            },
        }

        return success_response(
            data=response_data,
            message="Login successful",
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomUser.objects.get(email=email)
            send_password_reset_email(user)
        except CustomUser.DoesNotExist:
            return error_response(
                message="User with this email does not exists",
                error={"code": "User not found", "details": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "message": "If an account with this email exists, a reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return error_response(
                message="Invalid UID", status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return error_response(
                message="Invalid or expired token", status=status.HTTP_400_BAD_REQUEST
            )

        password = request.data.get("password")
        if not password:
            return error_response(
                message="Password is required", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user.set_password(password)
            user.save()

            serializer = LoginSerializer(
                data={
                    "email": user.email,
                    "password": password,
                }
            )
            serializer.is_valid(raise_exception=True)

            response_data = {
                "tokens": {
                    "access": serializer.validated_data["access"],
                    "refresh": serializer.validated_data["refresh"],
                },
                "user": {
                    "email": serializer.validated_data["email"],
                    "full_name": serializer.validated_data["full_name"],
                },
            }

            return success_response(
                data=response_data,
                message="Password has been reset successfully.",
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return error_response(
                message="Failed to reset password",
                error={"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    """
    Accepts a POST with {"refresh": "<refresh_token>"}.
    Blacklists the given refresh token so it can no longer be used.
    """

    permission_classes = IsAuthenticated

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh", None)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)
