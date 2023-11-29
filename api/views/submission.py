from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.serializers import *
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..sandbox.grader import PythonGrader
from time import sleep
from ..utility import regexMatching

from ..controllers.submission.submit_problem import *
from ..controllers.submission.get_submission_by_quries import *

@api_view([POST])
def submit_problem_view(request,problem_id,account_id):
    return submit_problem(problem_id,account_id,request)

@api_view([GET])
def all_submission_view(request):
    return get_submission_by_quries(request)
