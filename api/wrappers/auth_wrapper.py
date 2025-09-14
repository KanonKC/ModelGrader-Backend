from api.services.auth_service import verify_token
from api.utility import extract_bearer_token
from api.errors.common import InvalidTokenError

def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        token = extract_bearer_token(request)
        if not token:
            raise InvalidTokenError()
        is_verify = verify_token(token)
        if not is_verify:
            raise InvalidTokenError()
        return function(request, *args, **kwargs)
    return wrapper