# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict


# Create your views here.
@api_view([POST])
def create_problem(request,account_id):
    checked = checker(request.data['solution'],request.data['testcases'],request.data['time_limit'])

    if checked['has_error'] or checked['has_timeout']:
        return Response({'detail': 'Error during creating. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)
        
    problem = Problem(
        language = request.data['language'],
        account_id = Account.objects.get(account_id=account_id),
        title = request.data['title'],
        description = request.data['description'],
        solution = request.data['solution'],
        time_limit = request.data['time_limit']
    )
    problem.save()

    testcase_result = []
    for unit in checked['result']:
        testcase = Testcase(
            problem_id = problem,
            input = unit['input'],
            output = unit['output']
        )
        testcase.save()
        testcase_result.append(model_to_dict(testcase))
    return Response({'detail': 'Problem has been created!','problem': model_to_dict(problem),'testcase': testcase_result},status=status.HTTP_201_CREATED)

@api_view([GET])
def getall_problem(request):
    problem = Problem.objects.all()
    result = [model_to_dict(i) for i in problem]

    for i in result:
        i['creator'] = model_to_dict(Account.objects.get(account_id=i['account_id']))

    return Response({'result':result},status=status.HTTP_200_OK)
    

@api_view([GET])
def get_problem(request,problem_id: int):
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem_id=problem_id)
    result = model_to_dict(problem)
    account = Account.objects.get(account_id=result['account_id'])

    return Response({**result,'testcases':[model_to_dict(i) for i in testcases],'creator': model_to_dict(account)},status=status.HTTP_200_OK)