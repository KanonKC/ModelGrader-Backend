from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from api.errors.common import InternalServerError, InvalidFileError, BadRequestError
from api.errors.core.grader_exception import GraderException
from api.setup import problem_service
from api.utility import check_pdf
from api.services import s3_service
from api.utility import generate_random_string

@api_view([POST, GET])
@authentication_required
def all_problems_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = problem_service.create_problem(account_id, request)
        elif request.method == GET:
            result = problem_service.get_all_problems_by_account(account_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_problem_creator_view(request, problem_id: str, account_id: str):
    try:
        if request.method == GET:
            result = problem_service.get_problem(problem_id)
        elif request.method == PUT:
            result = problem_service.update_problem(problem_id, request)
        elif request.method == DELETE:
            problem_service.delete_problem(problem_id)
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
        
        if request.method == GET:
            result = problem_service.get_all_problem_with_best_submission(account_id)
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
        if request.method == GET:
            result = problem_service.get_problem_public(problem_id)
        elif request.method == PUT:
            result = problem_service.update_problem(problem_id, request)
        elif request.method == DELETE:
            problem_service.delete_problem(problem_id)
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
        if request.method == PUT:
            result = problem_service.update_group_permission_to_problem(problem_id, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def import_pdf_view(request, problem_id: int):
    try:
        if request.method == PUT:
            problem_service.import_elabsheet_problem(request, problem_id)
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


@api_view([GET])
def problem_pdf_url_view(request, problem_id: str):
    try:
        from api.models import Problem
        from api.services import s3_service
        problem = Problem.objects.get(problem_id=problem_id)
        if not problem.pdf_url:
            raise BadRequestError("This problem has no PDF.")
        url = s3_service.get_presigned_url(problem.pdf_url)
        return Response({"url": url}, status=200)
    except Problem.DoesNotExist:
        from api.errors.common import ItemNotFoundError
        return ItemNotFoundError().django_response()
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()


@api_view([POST])
@authentication_required
def upload_pdf_view(request):
    try:
        file = request.FILES.get("file")
        if not file:
            raise BadRequestError("No file provided.")
        if not check_pdf(file):
            raise InvalidFileError()
        filename_base = generate_random_string(12)
        key = s3_service.upload_pdf(file, filename_base)
        return Response({"key": key}, status=201)
    except GraderException as ge:
        return ge.django_response()
    except RuntimeError as e:
        return InternalServerError(e).django_response()
    except Exception as e:
        return InternalServerError(e).django_response()
