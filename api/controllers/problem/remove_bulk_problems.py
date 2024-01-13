from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def remove_bulk_problems(request):
    target = request.data.get("problem",[])
    problems = Problem.objects.filter(problem_id__in=target)
    problems.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    