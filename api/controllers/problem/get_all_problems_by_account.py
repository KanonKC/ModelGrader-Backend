from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_problems_by_account(account:Account):
    personalProblems = Problem.objects.filter(creator=account).order_by('-updated_date')
    for problem in personalProblems:
        problem.testcases = Testcase.objects.filter(problem=problem,deprecated=False)

    manageableProblems = Problem.objects.filter(problemgrouppermission__permission_manage_problems=True,problemgrouppermission__group__in=GroupMember.objects.filter(account=account).values_list("group",flat=True)).order_by('-updated_date')
    for problem in manageableProblems:
        problem.testcases = Testcase.objects.filter(problem=problem,deprecated=False)

    # problem_ser = ProblemPopulateTestcaseSerializer(problems,many=True)
    personalSerialize = ProblemPopulateTestcaseSerializer(personalProblems,many=True)
    manageableSerialize = ProblemPopulateTestcaseSerializer(manageableProblems,many=True)

    return Response({"problems":personalSerialize.data,"manageable_problems":manageableSerialize.data},status=status.HTTP_200_OK)