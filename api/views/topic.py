from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

from ..controllers.topic.create_topic import *
from ..controllers.topic.get_topic import *
from ..controllers.topic.get_all_topics import *
from ..controllers.topic.update_topic import *
from ..controllers.topic.delete_topic import *
from ..controllers.topic.add_collections_to_topic import *
from ..controllers.topic.remove_collections_from_topic import *
from ..controllers.topic.get_all_topics_by_account import *
from ..controllers.topic.update_collections_to_topic import *
from ..controllers.topic.get_topic_public import *
from ..controllers.topic.update_groups_permission_to_topic import *
from ..controllers.topic.get_all_accessed_topics_by_account import *
from ..permissions.topic import *

@api_view([POST,GET])
@parser_classes([MultiPartParser,FormParser])
def all_topics_creator_view(request,account_id :int):
    account = Account.objects.get(account_id=account_id)
    if request.method == POST:
        return create_topic(account_id,request)
    elif request.method == GET:
        return get_all_topics_by_account(account,request)

@api_view([GET,PUT,DELETE])
def one_topic_creator_view(request,account_id:str,topic_id:str):
    topic = Topic.objects.get(topic_id=topic_id)
    account = Account.objects.get(account_id=account_id)
    if not canManageTopic(topic,account):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == GET:
        return get_topic(topic)
    elif request.method == PUT:
        return update_topic(topic,request)
    elif request.method == DELETE:
        return delete_topic(topic)

@api_view([GET])
def all_topics_view(request):
    return get_all_topics(request)

@api_view([GET,PUT,DELETE])
def one_topic_view(request,topic_id:str):
    if request.method == GET:
        return get_topic_public(topic_id,request)
    elif request.method == PUT:
        return update_topic(topic_id,request)
    elif request.method == DELETE:
        return delete_topic(topic_id)

@api_view([PUT])
def topic_collections_view(request,topic_id:str,method:str):

    topic = Topic.objects.get(topic_id=topic_id)

    if method == "add":
        return add_collections_to_topic(topic_id,request)
    elif method == "remove":
        return remove_collections_from_topic(topic_id,request)
    elif method == "update":
        return update_collections_to_topic(topic,request)

@api_view([POST,PUT])
def account_access(request,topic_id:str):
    topic = Topic.objects.get(topic_id=topic_id)
    target_accounts = Account.objects.filter(account_id__in=request.data['account_ids'])

    if request.method == POST:
        accessedAccounts = []
        for account in target_accounts:
            topic_account = TopicAccountAccess(
                topic = topic,
                account = account
            )
            topic_account.save()
            accessedAccounts.append(topic_account)
        
        serialize = TopicAccountAccessSerialize(accessedAccounts,many=True)

        return Response({
            "accounts": serialize.data
        },status=status.HTTP_201_CREATED)
    
    elif request.method == PUT:
        topicAccountAccesses = TopicAccountAccess.objects.filter(account_id__in=request.data['account_ids'])
        topicAccountAccesses.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view([PUT])
def topic_groups_view(request,account_id:int,topic_id:str):
    topic = Topic.objects.get(topic_id=topic_id)
    return update_groups_permission_to_topic(topic,request)

@api_view([GET])
def all_topics_access_view(request,account_id:str):
    account = Account.objects.get(account_id=account_id)
    return get_all_accessed_topics_by_account(account)