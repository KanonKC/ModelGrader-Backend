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
from ..controllers.submission.get_submissions_by_account_problem import *
from ..controllers.submission.submit_problem_on_topic import *
from ..controllers.submission.get_submissions_by_account_problem_in_topic import *
from ..controllers.submission.get_all_submissions_by_creator_problem import *


@api_view([POST,GET])
def account_problem_submission_view(request,problem_id,account_id):
    if request.method == POST:
        try:
            return submit_problem(account_id,problem_id,request)
        except Exception as e:
            print(e)
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
    if request.method == GET:
        return get_submissions_by_account_problem(account_id,problem_id)

@api_view([GET])
def creator_problem_submissions_view(request,account_id,problem_id):
    problem = Problem.objects.get(problem_id=problem_id)
    return get_all_submissions_by_creator_problem(problem)

@api_view([GET])
def all_submission_view(request):
    return get_submission_by_quries(request)

@api_view([POST,GET])
def topic_account_problem_submission_view(request,topic_id,account_id,problem_id):
    if request.method == POST:
        return submit_problem_on_topic(account_id,problem_id,topic_id,request)
    if request.method == GET:
        return get_submissions_by_account_problem_in_topic(account_id,problem_id,topic_id)

# @api_view([GET])
# def submission_account_problem_view(request,account_id:str,problem_id:str):
#     return get_submissions_by_account_problem(account_id,problem_id)