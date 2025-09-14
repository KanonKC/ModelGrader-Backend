from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from api.models import Account

class CustomRequest(HttpRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_token(self):
        """
        Extract bearer token from Authorization header.
        Returns None if no valid token is found.
        """
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
            return None
        except (AttributeError, IndexError):
            return None

    def get_account(self):
        """
        Get the Account object associated with the request token.
        Returns None if no account is found or no valid token exists.
        """
        token = self.get_token()
        if not token:
            return None
        
        try:
            return Account.objects.get(token=token)
        except ObjectDoesNotExist:
            return None

    def has_valid_token(self):
        """
        Check if the request has a valid token.
        """
        return self.get_token() is not None

    def is_authenticated(self):
        """
        Check if the request has a valid account associated with it.
        """
        return self.get_account() is not None