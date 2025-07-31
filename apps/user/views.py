import logging

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import OR, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.responses import error_response, success_response
from apps.user.emails.reset_email import send_password_reset_email
from apps.user.permissions.groups import (
    IsAnyAdmin,
    IsAssessmentAgency,
    IsValueChainPartner,
)
from apps.user.permissions.permissions import IsSameOrganizationOrAdmin

from .models import CustomUser
from .serializers import CustomUserSerializer, ForgotPasswordSerializer, LoginSerializer
from .services.lms import get_frappe_login_url

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_value_chain_partner() or user.is_assessment_agency():
            return CustomUser.objects.filter(organization=user.organization)
        return CustomUser.objects.all()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["retrieve", "partial_update"]:
            return [
                OR(IsAssessmentAgency(), OR(IsValueChainPartner(), IsAnyAdmin())),
                IsSameOrganizationOrAdmin(),
            ]
        return False


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: openapi.Response(description="Login successful")},
    )
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
                "type": serializer.validated_data["type"],
                "organization": serializer.validated_data["organization"],
            },
        }

        return success_response(
            data=response_data,
            message="Login successful",
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={200: openapi.Response(description="Sent Password Reset email")},
    )
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
                    "type": serializer.validated_data["type"],
                    "organization": serializer.validated_data["organization"],
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

    permission_classes = (IsAuthenticated,)

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


class LMSUserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "get_login_url":
            return [IsAssessmentAgency()]
        return False

    @swagger_auto_schema(
        operation_description="Get one-time login URL from Frappe LMS.",
        responses={
            200: openapi.Response(description="Returns a one-time login URL"),
            400: "Bad Request",
            502: "Bad Gateway",
            500: "Internal Server Error",
        },
    )
    @action(detail=False, methods=["get"], url_path="login-url")
    def get_login_url(self, request):
        """
        Get one-time login URL from Frappe LMS for the authenticated user.
        """
        user_email = getattr(request.user, "email", None)

        if not user_email:
            return error_response(
                message="User email not found",
                error={
                    "code": "USER_EMAIL_NOT_FOUND",
                    "details": "user email not in request",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = get_frappe_login_url(user_email)
            message = response.get("message")
            login_url = message.get("login_url") if message else None
            return success_response(
                data={"url": login_url}, message="Login URL fetched successfully"
            )
        except ValidationError as e:
            logger.error(f"LMS configuration error: {e}")
            return error_response(
                message="Server misconfigured",
                error={"code": "LMS_CONFIG_ERROR", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"LMS request failed: {e}")
            return error_response(
                message="Failed to connect to LMS",
                error={"code": "LMS_CONNECTION_FAILED", "details": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except (ValueError, AttributeError, TypeError) as e:
            logger.exception(f"Invalid response from LMS: {e}")
            return error_response(
                message="Invalid LMS response",
                error={"code": "LMS_RESPONSE_INVALID", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
