from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_collection(collection_id:str):
    
    collection = Collection.objects.get(collection_id=collection_id)
    # problems = Problem.objects.filter(collectionproblem__collection_id=collection_id)
    collection.problems = CollectionProblem.objects.filter(collection=collection).order_by('order')
    collection.group_permissions = CollectionGroupPermission.objects.filter(collection=collection)
    
    # collection_ser = CollectionSerializer(collection)
    # collectionProblems_ser = CollectionProblemPopulateProblemSecureSerializer(collectionProblems,many=True)

    serializer = CollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(collection)
    

    return Response(serializer.data ,status=status.HTTP_200_OK)