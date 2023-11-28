from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_collection(collection_id:int):
    
    collection = Collection.objects.get(collection_id=collection_id)
    # problems = Problem.objects.filter(collectionproblem__collection_id=collection_id)
    collectionProblems = CollectionProblem.objects.filter(collection=collection)
    
    collection_ser = CollectionSerializer(collection)
    populated_problems = []
    for col_prob in collectionProblems:
        col_prob_serialize = CollectionProblemSerializer(col_prob)
        prob_serialize = ProblemSerializer(col_prob.problem)
        populated_problems.append({**col_prob_serialize.data,**prob_serialize.data})

    return Response({
        **collection_ser.data,
        'problems': sorted(populated_problems,key=lambda problem: problem['order'])
    } ,status=status.HTTP_200_OK)