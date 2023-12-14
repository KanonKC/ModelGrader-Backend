from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_collection(collection_id:int,request):
    collection = Collection.objects.get(collection_id=collection_id)
    collection_ser = CollectionSerializer(collection,data=request.data,partial=True)
    if collection_ser.is_valid():
        collection.updated_date = timezone.now()
        collection_ser = CollectionSerializer(collection,data=request.data,partial=True)
        collection_ser.save()
        return Response(collection_ser.data,status=status.HTTP_200_OK)
    else:
        return Response(collection_ser.errors,status=status.HTTP_400_BAD_REQUEST)
