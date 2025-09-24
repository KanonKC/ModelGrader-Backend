from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from api.errors.common import InternalServerError, BadRequestError
from api.errors.core.grader_exception import GraderException
from api.setup import group_service

@api_view([POST, GET])
@authentication_required
def all_groups_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = group_service.create_group(account_id, request)
        elif request.method == GET:
            result = group_service.get_all_groups_by_account(account_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_group_view(request, group_id: str):
    try:
        if request.method == GET:
            result = group_service.get_group(group_id, request)
        elif request.method == PUT:
            result = group_service.update_group(group_id, request)
        elif request.method == DELETE:
            group_service.delete_group(group_id)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT, POST])
@authentication_required
def group_members_view(request, group_id: str, method: str):
    try:
        if method == "add":
            result = group_service.add_members_to_group(group_id, request)
        elif method == "update":
            result = group_service.update_members_to_group(group_id, request)
        else:
            raise BadRequestError(f"Invalid method: {method}")
            
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
