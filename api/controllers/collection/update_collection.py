from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_collection(collection_id:str,request):
    collection = Collection.objects.get(collection_id=collection_id)

    collection.name = request.data.get('name',collection.name)
    collection.description = request.data.get('description',collection.description)
    collection.is_private = request.data.get('is_private',collection.is_private)
    collection.is_active = request.data.get('is_active',collection.is_active)
    collection.updated_date = timezone.now()

    collection.save()
    collection_ser = CollectionSerializer(collection)

    return Response(collection_ser.data,status=status.HTTP_200_OK)
