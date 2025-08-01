# apps/authentication/tokens.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["full_name"] = user.full_name

        # Add user role
        token["user_role"] = user.groups.first().name if user.groups.exists() else None

        return token
