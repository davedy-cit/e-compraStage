"""Custom JWT authentication that fetches the actual AuthUser model."""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from accounts.models import AuthUser


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that fetches the AuthUser model instance
    instead of using the default TokenUser.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_model = AuthUser

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[settings.SIMPLE_JWT["USER_ID_CLAIM"]]
        except KeyError as err:
            raise InvalidToken("Token contained no recognizable user identification") from err

        try:
            user = AuthUser.objects.get(**{settings.SIMPLE_JWT["USER_ID_FIELD"]: user_id})
        except AuthUser.DoesNotExist as err:
            raise AuthenticationFailed("User not found", code="user_not_found") from err

        if not self.user_can_authenticate(user):
            raise AuthenticationFailed(
                "User is inactive", code="user_inactive"
            )

        return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        an is_active field are considered active.
        """
        is_active = getattr(user, "is_active", None)
        if is_active is not None:
            return bool(is_active)
        return True
