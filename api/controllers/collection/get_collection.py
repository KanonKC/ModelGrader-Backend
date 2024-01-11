from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_collection(collection:Collection):
    
    collection.problems = CollectionProblem.objects.filter(collection=collection).order_by('order')
    collection.group_permissions = CollectionGroupPermission.objects.filter(collection=collection)

    for cp in collection.problems:
        cp.problem.testcases = Testcase.objects.filter(problem=cp.problem,deprecated=False)
        cp.problem.group_permissions = ProblemGroupPermission.objects.filter(problem=cp.problem)

    serializer = CollectionPopulateCollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupAndCollectionGroupPermissionsPopulateGroupSerializer(collection)
    

    return Response(serializer.data ,status=status.HTTP_200_OK)