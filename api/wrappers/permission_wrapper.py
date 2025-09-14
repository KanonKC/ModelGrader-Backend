from api.errors.common import PermissionDeniedError
from api.permissions.topic import canManageTopic
from api.services.permission_service import canManageProblem
from api.utility import extract_bearer_token


def manage_problem_permission(function):
    def wrapper(request, *args, **kwargs):
        token = extract_bearer_token(request)
        if canManageProblem(token, kwargs['problem_id']):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDeniedError()
    return wrapper

def manage_topic_permission(function):
    def wrapper(request, *args, **kwargs):
        token = extract_bearer_token(request)
        if canManageTopic(*args):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDeniedError()
    return wrapper