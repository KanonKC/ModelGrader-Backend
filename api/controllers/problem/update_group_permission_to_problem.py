from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_group_permission_to_problem(problem:Problem,request):
    ProblemGroupPermission.objects.filter(problem=problem).delete()

    problem_group_permissions = []
    for group_request in request.data['groups']:
        group = Group.objects.get(group_id=group_request['group_id'])
        problem_group_permissions.append(
            ProblemGroupPermission(
                problem=problem,
                group=group,
                **group_request
        ))

    ProblemGroupPermission.objects.bulk_create(problem_group_permissions)

    problem.group_permissions = problem_group_permissions
    problem.testcases = Testcase.objects.filter(problem=problem)
    
    serialize = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(problem)
    return Response(serialize.data,status=status.HTTP_202_ACCEPTED)