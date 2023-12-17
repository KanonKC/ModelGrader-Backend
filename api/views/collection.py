from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
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


@api_view([POST,GET])
def all_collections_account_view(request,account_id:int):
    if request.method == POST:
        return create_collection(account_id,request)
    if request.method == GET:
        return get_all_collections_by_account(account_id)

@api_view([GET,PUT,DELETE])
def one_collection_account_view(request,collection_id:int):
    if request.method == GET:
        return get_collection(collection_id)
    if request.method == PUT:
        return update_collection(collection_id,request)
    if request.method == DELETE:
        return delete_collection(collection_id)

@api_view([GET])
def all_collections_view(request):
    return get_all_collections(request)

@api_view([GET,PUT,DELETE])
def one_collection_view(request,collection_id:int):
    if request.method == GET:
        return get_collection(collection_id)
    if request.method == PUT:
        return update_collection(collection_id,request)
    if request.method == DELETE:
        return delete_collection(collection_id)

@api_view([PUT])
def collection_problems_view(request,collection_id:int,method:str):

    collection = Collection.objects.get(collection_id=collection_id)

    if method == "add":
        return add_problems_to_collection(collection,request)
    if  method == "remove":
        return remove_problems_from_collection(collection,request)
    if method == "update":
        return update_problems_to_collection(collection,request)