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
    collectionProblems = CollectionProblem.objects.filter(collection=collection).order_by('order')
    
    collection_ser = CollectionSerializer(collection)
    collectionProblems_ser = CollectionProblemPopulateProblemSecureSerializer(collectionProblems,many=True)
    # populated_problems = []
    # for col_prob in collectionProblems:
    #     col_prob_serialize = CollectionProblemPopulateProblemSecureSerializer(col_prob)
    #     # prob_serialize = ProblemSerializer(col_prob.problem)
    #     populated_problems.append(col_prob_serialize.data)

    return Response({
        **collection_ser.data,
        'problems': collectionProblems_ser.data
    } ,status=status.HTTP_200_OK)