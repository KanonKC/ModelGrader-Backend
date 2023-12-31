from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_problems_by_account(account_id:str):
    problems = Problem.objects.filter(creator=account_id).order_by('-updated_date')

    for problem in problems:
        problem.testcases = Testcase.objects.filter(problem=problem,deprecated=False)

    problem_ser = ProblemPopulateTestcaseSerializer(problems,many=True)
    return Response({"problems":problem_ser.data},status=status.HTTP_200_OK)