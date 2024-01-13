from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader,Grader,ProgramGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from ...utility import regexMatching
from time import sleep
from .submit_problem import *

def submit_problem_on_topic(account_id:str,problem_id:str,topic_id:str,request):
    return submit_problem_function(account_id,problem_id,topic_id,request)