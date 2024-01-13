from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader,RuntimeResult
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def create_problem(account_id:str,request):
    account = Account.objects.get(account_id=account_id)
    
    running_result = PythonGrader(request.data['solution'],request.data['testcases'],1,1.5).generate_output()

    # if not running_result.runnable:
    #     return Response({'detail': 'Error during creating. Your code may has an error/timeout!','output': running_result.getResult()},status=status.HTTP_406_NOT_ACCEPTABLE)
        
    problem = Problem(
        language = request.data['language'],
        creator = account,
        title = request.data['title'],
        description = request.data['description'],
        solution = request.data['solution'],
        time_limit = request.data['time_limit'],
        allowed_languages = request.data['allowed_languages'],
    )
    problem.save()

    testcases_result = []
    for unit in running_result.data:
        testcases_result.append(
            Testcase(
                problem = problem,
                input = unit.input,
                output = unit.output,
                runtime_status = unit.runtime_status
        ))

    Testcase.objects.bulk_create(testcases_result)

    problem_serialize = ProblemSerializer(problem)
    testcases_serialize = TestcaseSerializer(testcases_result,many=True)

    return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_201_CREATED)
