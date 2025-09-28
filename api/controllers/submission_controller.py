from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from api.errors.common import InternalServerError, BadRequestError
from api.errors.core.grader_exception import GraderException
import api.services.submission.submission_service as submission_service

@api_view([POST, GET])
@authentication_required
def creator_problem_submissions_view(request, account_id: str, problem_id: str):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if request.method == GET:
            result = submission_service.get_all_submissions_by_creator_problem(problem, request)
        elif request.method == POST:
            result = submission_service.submit_problem(account_id, problem_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([POST, GET])
@authentication_required
def topic_account_problem_submission_view(request, account_id: str, topic_id: str, problem_id: str):
    try:
        if request.method == GET:
            result = submission_service.get_submissions_by_account_problem_in_topic(account_id, problem_id, topic_id)
        elif request.method == POST:
            result = submission_service.submit_problem_on_topic(account_id, problem_id, topic_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def account_problem_submission_view(request, problem_id: str, account_id: str):
    try:
        if request.method == GET:
            result = submission_service.get_submissions_by_account_problem(account_id, problem_id)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def all_submission_view(request):
    try:
        if request.method == GET:
            result = submission_service.get_submission_by_quries(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
