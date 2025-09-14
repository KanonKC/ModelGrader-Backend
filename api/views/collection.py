from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

from ..controllers.collection.create_collection import *
from ..controllers.collection.get_collection import *
from ..controllers.collection.get_all_collections import *
from ..controllers.collection.update_collection import *
from ..controllers.collection.delete_collection import *
from ..controllers.collection.add_problems_to_collection import *
from ..controllers.collection.remove_problems_from_collection import *
from ..controllers.collection.get_all_collections_by_account import *
from ..controllers.collection.update_problems_to_collection import *
from ..controllers.collection.update_group_permissions_collection import *

@api_view([POST,GET])
@authentication_required
def all_collections_creator_view(request,account_id:str):
    if request.method == POST:
        return create_collection(account_id,request)
    if request.method == GET:
        return get_all_collections_by_account(account_id)

@api_view([GET,PUT,DELETE])
@authentication_required
def one_collection_creator_view(request,account_id:int,collection_id:str):
    collection = Collection.objects.get(collection_id=collection_id)
    if request.method == GET:
        return get_collection(collection)
    if request.method == PUT:
        return update_collection(collection,request)
    if request.method == DELETE:
        return delete_collection(collection)

@api_view([GET])
@authentication_required
def all_collections_view(request):
    return get_all_collections(request)

@api_view([GET,PUT,DELETE])
@authentication_required
def one_collection_view(request,collection_id:str):
    if request.method == GET:
        return get_collection(collection_id)
    if request.method == PUT:
        return update_collection(collection_id,request)
    if request.method == DELETE:
        return delete_collection(collection_id)

@api_view([PUT])
@authentication_required
def collection_problems_view(request,collection_id:str,method:str):

    collection = Collection.objects.get(collection_id=collection_id)

    if method == "add":
        return add_problems_to_collection(collection,request)
    if  method == "remove":
        return remove_problems_from_collection(collection,request)
    if method == "update":
        return update_problems_to_collection(collection,request)
    
@api_view([PUT])
@authentication_required
def collection_groups_view(request,account_id:int,collection_id:str):
    collection = Collection.objects.get(collection_id=collection_id)
    if request.method == PUT:
        return update_group_permissions_collection(collection,request)