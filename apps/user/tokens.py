# apps/authentication/tokens.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.organization.serializers import OrganizationSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        org_data = (
            OrganizationSerializer(user.organization).data
            if user.organization
            else None
        )
        token = super().get_token(user)
        # embed organization type & full_name into the signed payload
        token["user_type"] = user.organization.type
        token["full_name"] = user.full_name
        token["organization"] = org_data

        # Add user role
        token["user_role"] = user.groups.first().name if user.groups.exists() else None

        return token
