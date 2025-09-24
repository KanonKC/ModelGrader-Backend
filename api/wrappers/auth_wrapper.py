from api.utility import extract_bearer_token
from api.errors.common import InvalidTokenError
from api.setup import auth_service

def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        token = extract_bearer_token(request)
        if not token:
            return InvalidTokenError().django_response()
        is_verify = auth_service.verify_token(token)
        if not is_verify:
            return InvalidTokenError().django_response()
        return function(request, *args, **kwargs)
    return wrapper