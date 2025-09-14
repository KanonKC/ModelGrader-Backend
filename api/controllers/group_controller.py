from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from api.errors.common import InternalServerError, BadRequestError
from api.errors.core.grader_exception import GraderException
import api.services.group.group_service as group_service

@api_view([POST, GET])
@authentication_required
def all_groups_creator_view(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        if request.method == POST:
            result = group_service.create_group(account, request)
        elif request.method == GET:
            result = group_service.get_all_groups_by_account(account, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_group_view(request, group_id: str):
    try:
        group = Group.objects.get(group_id=group_id)
        if request.method == GET:
            result = group_service.get_group(group, request)
        elif request.method == PUT:
            result = group_service.update_group(group, request)
        elif request.method == DELETE:
            group_service.delete_group(group, request)
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
        group = Group.objects.get(group_id=group_id)
        
        if method == "add":
            result = group_service.add_members_to_group(group, request)
        elif method == "update":
            result = group_service.update_members_to_group(group, request)
        else:
            raise BadRequestError(f"Invalid method: {method}")
            
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
