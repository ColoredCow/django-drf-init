from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ForgotPasswordView,
    LMSUserViewSet,
    LoginView,
    LogoutView,
    ResetPasswordView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"lms", LMSUserViewSet, basename="lms-user")
router.register(r"", UserViewSet)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path(
        "reset-password/<uidb64>/<token>/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
