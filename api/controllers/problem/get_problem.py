from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_problem(problem_id:int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
    except Problem.DoesNotExist:
        return Response({'detail': "Problem doesn't exist!"},status=status.HTTP_404_NOT_FOUND)
    testcases = Testcase.objects.filter(problem_id=problem_id,deprecated=False)
    problem_serialize = ProblemPopulateAccountSerializer(problem)
    testcases_serialize = TestcaseSerializer(testcases,many=True)
    return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_200_OK)
    