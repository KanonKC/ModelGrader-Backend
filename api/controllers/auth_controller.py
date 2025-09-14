from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
from ..constant import POST,PUT
import api.services.auth_service as auth_service

@api_view([POST])
def login(request):
    try:
        result = auth_service.login(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([POST])
def logout(request):
    try:
        result = auth_service.logout(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
def authorization(request):
    try:
        result = auth_service.authorization(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()