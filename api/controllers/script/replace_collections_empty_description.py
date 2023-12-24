from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict

def replace_collections_empty_description(request):
    collections = Collection.objects.all()
    for collection in collections:
        collection.description = '[{"id":"1","type":"p","children":[{"text":"Just course"}]}]'
        collection.save()
    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)
