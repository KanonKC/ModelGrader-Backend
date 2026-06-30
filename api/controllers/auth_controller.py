from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
from api.services.auth.cookie_service import set_refresh_cookie, get_refresh_token_from_cookie, clear_refresh_cookie
from ..constant import POST, PUT
from api.setup import auth_service


@api_view([POST])
def login(request):
    try:
        result = auth_service.login(request)
        refresh_token = result.pop("refresh_token")
        response = Response(result, status=200)
        set_refresh_cookie(response, refresh_token)
        return response
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()


@api_view([POST])
def logout(request):
    response = Response({"result": True}, status=200)
    clear_refresh_cookie(response)
    return response


@api_view([PUT])
def authorization(request):
    try:
        result = auth_service.authorization(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()


@api_view([POST])
def token_refresh(request):
    try:
        refresh_token = get_refresh_token_from_cookie(request)
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=401)
        result = auth_service.refresh_from_token(refresh_token)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
