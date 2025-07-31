from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organization.serializers import OrganizationSerializer

from .models import CustomUser
from .tokens import MyTokenObtainPairSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "full_name",
            "designation",
            "email",
            "phone",
            "organization",
        )
        read_only_fields = ("frappe_lms_user_created_on",)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        User = get_user_model()
        try:
            user = User.objects.select_related("organization").get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        refresh = MyTokenObtainPairSerializer.get_token(user)
        access = refresh.access_token

        org_data = (
            OrganizationSerializer(user.organization).data
            if user.organization
            else None
        )

        return {
            "access": str(access),
            "refresh": str(refresh),
            "email": user.email,
            "full_name": user.full_name,
            "type": user.organization.type if user.organization else None,
            "organization": org_data,
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
