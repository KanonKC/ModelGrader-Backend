# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from ..models import *
from .auth_service import verify_token, getAccountByToken
from .permission_service import canManageProblem
from ..utility import generate_random_string, check_pdf
from .service_result import ServiceResult
from django.forms.models import model_to_dict
from ..errors.common import *
from ..errors.grader import *
from api.sandbox.grader import Grader
from ..serializers import *

def verifyProblem(problem_id):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if not problem:
            return False
        return True
    except Problem.DoesNotExist:
        return False

def get_problem(problem_id, request, token, is_secure):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        testcases = Testcase.objects.filter(problem=problem,deprecated=False)
        group_permissions = ProblemGroupPermission.objects.filter(problem=problem)
        domain = request.get_host()
        pdf_filename = problem.pdf_url
        if is_secure:
            problem.pdf_url = f"https://{domain}/media/import-pdf/{pdf_filename}" if pdf_filename else ""
        else :
            problem.pdf_url = f"http://{domain}/media/import-pdf/{pdf_filename}" if pdf_filename else ""
        serialized_group_permissions = []
        for group_permission in group_permissions:
            group = model_to_dict(group_permission.group)
            serialized_group_permission = model_to_dict(group_permission)
            serialized_group_permission['group'] = group
            serialized_group_permissions.append(serialized_group_permission)
        return {
            **model_to_dict(problem),
            "testcases": [model_to_dict(testcase) for testcase in testcases],
            "group_permissions": serialized_group_permissions,
        }
    except Problem.DoesNotExist:
        raise ItemNotFoundError()
    except Exception as e:
        print("Error: ", e)
        raise e


def upload_pdf(problem_id, file, token):
    # Get user from Token
    # If not access return ... -> verify
    # Get problem from ID
    # Store file at media/import-pdf
    # Write Problem database -> pdfFilename

    """
    204: No content
    401: Unauthorized - No token / Token expired
    403: Forbidden - No permission (User found)
    500: Internal Server Error
    """
    problem = Problem.objects.get(problem_id=problem_id) if verifyProblem(problem_id) else None
    if not verify_token(token):
        raise InvalidTokenError()
    if not problem:
        raise ItemNotFoundError()
    if not canManageProblem(token, problem_id):
        raise PermissionDeniedError()
    if not check_pdf(file):
        raise InvalidFileError()
    try:
        file_name = "_".join(problem.title.split()) + "_" + generate_random_string()
        file_path = f"media/import-pdf/{file_name}.pdf"
        with open(file_path, 'wb') as f:
            f.write(file.read())
        problem.pdf_url = file_name + ".pdf"
        problem.save()
    except Exception as e:
        return ServiceResult.error(
            message=f"An error occurred while uploading the PDF: {str(e)}",
            errorType="internal_error"
        )
    return None

def get_problem_pdf(problem_id, token):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
        if not verify_token(token):
            raise InvalidTokenError()
        if not canManageProblem(token, problem_id):
            raise PermissionDeniedError()
        
        file_path = f"media/import-pdf/{problem.pdf_url}"
        pdf_file = open(file_path, 'rb')
        
        if not pdf_file:
            raise ItemNotFoundError()

        return pdf_file
    except Problem.DoesNotExist:
        raise ItemNotFoundError()
    except Exception as e:
        raise e 
    
def create_problem(data, token):
    try:
        account = getAccountByToken(token)
        running_result = Grader[data['language']](data['solution'],data['testcases'],1,1.5).generate_output()

        problem = Problem(
            language = data['language'],
            creator = account,
            title = data['title'],
            description = data['description'],
            solution = data['solution'],
            time_limit = data['time_limit'],
            allowed_languages = data['allowed_languages'],
            view_mode = data['view_mode'],
        )

        testcases = []
        for unit in running_result.data:
            testcases.append(
                Testcase(
                    problem = problem,
                    input = unit.input,
                    output = unit.output,
                    runtime_status = unit.runtime_status,
                )
            )

        problem_serialize = ProblemSerializer(problem)
        testcases_serialize = TestcaseSerializer(testcases,many=True)

        problem.save()
        Testcase.objects.bulk_create(testcases)

        return problem_serialize, testcases_serialize
    except Exception as e:
        raise e
        
def update_problem(data, token, problem_id):
    try:
        problem = Problem.objects.get(problem_id=problem_id)

        if not verify_token(token):
            raise InvalidTokenError()
        
        if not canManageProblem(token, problem_id):
            raise PermissionDeniedError()
        
        testcases = Testcase.objects.filter(problem_id=problem_id, deprecated=False)
        
        problem.title = data.get("title",problem.title)
        problem.language = data.get("language",problem.language)
        problem.description = data.get("description",problem.description)
        problem.solution = data.get("solution",problem.solution)
        problem.time_limit = data.get("time_limit",problem.time_limit)  
        problem.is_private = data.get("is_private",problem.is_private)
        problem.allowed_languages = data.get("allowed_languages",problem.allowed_languages)
        problem.view_mode = data.get("view_mode", problem.view_mode)

        problem.updated_date = timezone.now()
        testcase_result = None
        if 'testcases' in data:
            running_result = Grader[data['language']](problem.solution,data['testcases'],1,1.5).generate_output()

            for testcase in testcases:
                testcase.deprecated = True
                testcase.save()
            testcase_result = []
            for unit in running_result.data:
                new_testcase = Testcase(
                    problem = problem,
                    input = unit.input,
                    output = unit.output,
                    runtime_status = unit.runtime_status
                )
                new_testcase.save()
                testcase_result.append(new_testcase)
        
        if 'solution' in data:
            testcases = Testcase.objects.filter(problem=problem,deprecated=False)
            program_input = [i.input for i in testcases]
            running_result = Grader[data['language']](problem.solution,program_input,1,1.5).generate_output()

            if not running_result.runnable:
                raise CodeExecutionError()
            
        serialized_problem = ProblemSerializer(problem).data
        serialized_testcases = TestcaseSerializer(testcase_result or testcases, many=True).data

        problem.save()
        return serialized_problem, serialized_testcases
    except Problem.DoesNotExist:
        raise ItemNotFoundError()
    except Exception as e:
        raise e
