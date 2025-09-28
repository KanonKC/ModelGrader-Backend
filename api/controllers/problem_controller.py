from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
import api.services.problem.problem_service as problem_service

@api_view([POST, GET])
@authentication_required
def all_problems_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = problem_service.create_problem(account_id, request)
        elif request.method == GET:
            account = Account.objects.get(account_id=account_id)
            result = problem_service.get_all_problems_by_account(account, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_problem_creator_view(request, problem_id: str, account_id: str):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if request.method == GET:
            result = problem_service.get_problem(problem)
        elif request.method == PUT:
            result = problem_service.update_problem(problem, request)
        elif request.method == DELETE:
            problem_service.delete_problem(problem)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, DELETE])
@authentication_required
def all_problems_view(request):
    try:
        account_id = request.GET.get("account_id", None)
        try:
            account = Account.objects.get(account_id=account_id)
        except:
            account = None
        
        if request.method == GET:
            result = problem_service.get_all_problem_with_best_submission(account)
        elif request.method == DELETE:
            problem_service.remove_bulk_problems(request)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
def one_problem_view(request, problem_id: int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if request.method == GET:
            result = problem_service.get_problem_public(problem)
        elif request.method == PUT:
            result = problem_service.update_problem(problem, request)
        elif request.method == DELETE:
            problem_service.delete_problem(problem)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([POST])
@authentication_required
def validation_view(request):
    try:
        if request.method == POST:
            result = problem_service.validate_program(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def problem_in_topic_account_view(request, account_id: str, topic_id: str, problem_id: str):
    try:
        if request.method == GET:
            result = problem_service.get_problem_in_topic_with_best_submission(account_id, topic_id, int(problem_id))
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def problem_group_view(request, account_id: int, problem_id: int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if request.method == PUT:
            result = problem_service.update_group_permission_to_problem(problem, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def import_pdf_view(request, problem_id: int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if request.method == PUT:
            problem_service.import_elabsheet_problem(request, problem)
            return Response(status=204)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def all_problems_list_view(request):
    try:
        if request.method == GET:
            result = problem_service.get_all_problems(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
