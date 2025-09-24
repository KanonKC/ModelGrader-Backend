from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from api.errors.common import InternalServerError, BadRequestError
from api.errors.core.grader_exception import GraderException
from api.setup import collection_service

@api_view([POST, GET])
@authentication_required
def all_collections_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = collection_service.create_collection(account_id, request)
        elif request.method == GET:
            result = collection_service.get_all_collections_by_account(account_id)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_collection_creator_view(request, collection_id: str, account_id: str):
    try:
        if request.method == GET:
            result = collection_service.get_collection(collection_id)
        elif request.method == PUT:
            result = collection_service.update_collection(collection_id, request)
        elif request.method == DELETE:
            collection_service.delete_collection(collection_id)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
def all_collections_view(request):
    try:
        if request.method == GET:
            result = collection_service.get_all_collections(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
def one_collection_view(request, collection_id: str):
    try:
        if request.method == GET:
            result = collection_service.get_collection(collection_id)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def collection_groups_view(request, account_id: str, collection_id: str):
    try:
        if request.method == PUT:
            result = collection_service.update_group_permissions_collection(collection_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT, POST])
@authentication_required
def collection_problems_view(request, collection_id: str, method: str):
    try:
        
        if method == "add":
            result = collection_service.add_problems_to_collection(collection_id, request)
        elif method == "update":
            result = collection_service.update_problems_to_collection(collection_id, request)
        elif method == "remove":
            collection_service.remove_problems_from_collection(collection_id, request)
            return Response(status=204)
        else:
            raise BadRequestError(f"Invalid method: {method}")
            
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
