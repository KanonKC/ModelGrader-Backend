from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_problem_public(problem:Problem):
    serialize = ProblemPopulateAccountSecureSerializer(problem)
    return Response(serialize.data,status=status.HTTP_200_OK)
    