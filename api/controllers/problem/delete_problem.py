from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def delete_problem(problem:Problem):
    # try:
    #     problem = Problem.objects.get(problem_id=problem_id)
    # except Problem.DoesNotExist:
    #     return Response({'detail': "Problem doesn't exist!"},status=status.HTTP_404_NOT_FOUND)
    testcases = Testcase.objects.filter(problem_id=problem_id)

    problem.delete()
    testcases.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)