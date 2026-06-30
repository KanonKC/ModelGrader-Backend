from api.utility import extract_bearer_token
from api.errors.common import InvalidTokenError
from api.services.auth.jwt_service import verify_access_token
import jwt


def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        token = extract_bearer_token(request)
        if not token:
            return InvalidTokenError().django_response()
        try:
            verify_access_token(token)
        except jwt.ExpiredSignatureError:
            return InvalidTokenError().django_response()
        except jwt.InvalidTokenError:
            return InvalidTokenError().django_response()
        return function(request, *args, **kwargs)
    return wrapper
