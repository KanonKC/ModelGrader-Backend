# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

from ..controllers.problem.create_problem import *
from ..controllers.problem.update_problem import *
from ..controllers.problem.delete_problem import *
from ..controllers.problem.get_problem import *
from ..controllers.problem.get_all_problems import *
from ..controllers.problem.remove_bulk_problems import *
from ..controllers.problem.get_all_problems_by_account import *
from ..controllers.problem.validate_program import *
from ..controllers.problem.get_all_problem_with_best_submission import *
from ..controllers.problem.get_problem_in_topic_with_best_submission import *
from ..controllers.problem.update_group_permission_to_problem import *
from ..controllers.problem.get_problem_public import *
from ..controllers.problem.import_elabsheet_problem import *


# Create your views here.
@api_view([POST,GET])
def all_problems_creator_view(request,account_id):
    if  request.method == POST:
        return create_problem(account_id,request)
    if request.method == GET:
        return get_all_problems_by_account(account_id,request)

@api_view([GET,PUT,DELETE])
def one_problem_creator_view(request,problem_id:str,account_id:str):
    problem = Problem.objects.get(problem_id=problem_id)
    if request.method == GET:
        return get_problem(problem)
    elif request.method == PUT:
        return update_problem(problem,request)
    elif request.method == DELETE:
        return delete_problem(problem)

@api_view([GET,DELETE])
def all_problems_view(request):
    account_id = request.GET.get("account_id",None)
    try:
        account = Account.objects.get(account_id=account_id)
    except:
        account = None
    if request.method == GET:
        return get_all_problem_with_best_submission(account)
    elif request.method == DELETE:
        return remove_bulk_problems(request)
    
@api_view([GET,PUT,DELETE])
def one_problem_view(request,problem_id: int):
    problem = Problem.objects.get(problem_id=problem_id)
    if request.method == GET:
        return get_problem_public(problem)
    elif request.method == PUT:
        return update_problem(problem_id,request)
    elif request.method == DELETE:
        return delete_problem(problem_id)
    
@api_view([POST])
def validation_view(request):
    if request.method == POST:
        return validate_program(request)
    
@api_view([GET])
def problem_in_topic_account_view(request,account_id:str,topic_id:str,problem_id:str):
    if request.method == GET:
        return get_problem_in_topic_with_best_submission(account_id,topic_id,problem_id)
    
@api_view([PUT])
def problem_group_view(request,account_id:int,problem_id:int):
    problem = Problem.objects.get(problem_id=problem_id)
    if request.method == PUT:
        return update_group_permission_to_problem(problem,request)
    
# @api_view([POST])
# def import_elabsheet_problem_view(request):
#     if request.method == POST:
#         print(request)

@api_view([PUT])
def import_pdf_view(request,problem_id:int):
    problem = Problem.objects.get(problem_id=problem_id)
    if request.method == PUT:
        return import_elabsheet_problem(request, problem)