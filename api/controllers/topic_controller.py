from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from api.errors.common import InternalServerError, BadRequestError
from api.errors.core.grader_exception import GraderException
import api.services.topic.topic_service as topic_service

@api_view([POST, GET])
@authentication_required
def all_topics_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = topic_service.create_topic(account_id, request)
        elif request.method == GET:
            account = Account.objects.get(account_id=account_id)
            result = topic_service.get_all_topics_by_account(account, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_topic_creator_view(request, topic_id: str, account_id: str):
    try:
        topic = Topic.objects.get(topic_id=topic_id)
        if request.method == GET:
            result = topic_service.get_topic(topic)
        elif request.method == PUT:
            result = topic_service.update_topic(topic, request)
        elif request.method == DELETE:
            topic_service.delete_topic(topic)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
def all_topics_view(request):
    try:
        if request.method == GET:
            result = topic_service.get_all_topics(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
def one_topic_view(request, topic_id: str):
    try:
        if request.method == GET:
            result = topic_service.get_topic_public(topic_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def all_topics_access_view(request, account_id: str):
    try:
        if request.method == GET:
            account = Account.objects.get(account_id=account_id)
            result = topic_service.get_all_accessed_topics_by_account(account)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def topic_groups_view(request, account_id: str, topic_id: str):
    try:
        topic = Topic.objects.get(topic_id=topic_id)
        if request.method == PUT:
            result = topic_service.update_groups_permission_to_topic(topic, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT, POST])
@authentication_required
def topic_collections_view(request, topic_id: str, method: str):
    try:
        if method == "add":
            result = topic_service.add_collections_to_topic(topic_id, request)
        elif method == "update":
            topic = Topic.objects.get(topic_id=topic_id)
            result = topic_service.update_collections_to_topic(topic, request)
        elif method == "remove":
            topic_service.remove_collections_from_topic(topic_id, request)
            return Response(status=204)
        else:
            raise BadRequestError(f"Invalid method: {method}")
            
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([POST])
@authentication_required
def account_access(request, topic_id: str):
    try:
        # This function would need to be implemented in topic_service
        # For now, returning empty response
        return Response(status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
