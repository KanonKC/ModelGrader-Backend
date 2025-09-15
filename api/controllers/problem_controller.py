# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import PUT, GET, POST
from rest_framework import status
from ..utility import extract_bearer_token, ERROR_TYPE_TO_STATUS
from ..services import problem_service
from ..errors.common import *
from django.http import FileResponse

@api_view([PUT])
def upload_pdf(request, problem_id:str):
    try:
        file = request.FILES.get('file')
        token = extract_bearer_token(request)
        if not token:
            raise InvalidTokenError()
        if not file:
            raise InvalidFileError()
        problem_service.upload_pdf(problem_id, file, token)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        if (isinstance(e, GraderException)):
            return Response({
                "status": e.status,
                "error": e.error
            }, status=e.status)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view([GET])
def get_problem_pdf(request, problem_id:str, token):
    """
    Get problem PDF file
    200: OK
    401: Unauthorized - No token / Token expired
    403: Forbidden - No permission
    404: Not Found - Problem not found
    500: Internal Server Error
    """
    try:
        pdf_file = problem_service.get_problem_pdf(problem_id, token)
        return FileResponse(pdf_file, content_type='application/pdf')
    except Exception as e:
        if (isinstance(e, GraderException)):
            return Response({
                "status": e.status,
                "error": e.error
            }, status=e.status)
        else :
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_problem(request, problem_id:str, token):
    try:
        problem = problem_service.get_problem(problem_id, request, token, request.is_secure())
        return Response(problem, status=status.HTTP_200_OK)
    except Exception as e:
        if (isinstance(e, GraderException)):
            return Response({
                "status": e.status,
                "error": e.error
            }, status=e.status)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view([POST])
def create_problem(request, token):
    """
    create problem
    201: Created
    401: Unauthorized - No token / Token expired
    403: Forbidden - No permission
    404: Not Found - Problem not found
    500: Internal Server Error
    """
    try:
        problem, testcases = problem_service.create_problem(request.data, token)
        return Response({**problem.data,'testcases': testcases.data},status=status.HTTP_201_CREATED)
    except Exception as e:
        if (isinstance(e, GraderException)):
            return Response({
                "status": e.status,
                "error": e.error
            }, status=e.status)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
def update_problem(request, problem_id, token):
    try:
        problem, testcases = problem_service.update_problem(request.data, token, problem_id)
        return Response({**problem,'testcases': testcases},status=status.HTTP_201_CREATED)
    except Exception as e:
        if (isinstance(e, GraderException)):
            return Response({
                "status": e.status,
                "error": e.error
            }, status=e.status)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view([GET, PUT])
def get_or_update_problem(request, problem_id, token):
    if request.method == GET:
        return get_problem(request, problem_id, token)
    elif request.method == PUT:
        return update_problem(request, problem_id, token)
    