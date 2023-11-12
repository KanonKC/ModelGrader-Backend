# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

# Create your views here.
@api_view([POST])
def create_problem(request,account_id):
    account = Account.objects.get(account_id=account_id)
    
    program_output = PythonGrader(request.data['solution'],request.data['testcases'],1,1.5).generate_output()
    for result in program_output:
        if result.runtime_status != "OK":
            return Response({'detail': 'Error during creating. Your code may has an error/timeout!','output': [dict(i) for i in program_output]},status=status.HTTP_406_NOT_ACCEPTABLE)
        
    problem = Problem(
        language = request.data['language'],
        account = account,
        title = request.data['title'],
        description = request.data['description'],
        solution = request.data['solution'],
        time_limit = request.data['time_limit']
    )
    problem.save()

    testcases_result = []
    for unit in program_output:
        testcases_result.append(
            Testcase(
                problem = problem,
                input = unit.input,
                output = unit.output
        ))

    Testcase.objects.bulk_create(testcases_result)

    problem_serialize = ProblemSerializer(problem)
    testcases_serialize = TestcaseSerializer(testcases_result,many=True)

    return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_201_CREATED)

@api_view([GET,DELETE])
def all_problem(request):
    if request.method == GET:

        problem = Problem.objects.all()

        get_private = int(request.query_params.get("private",0))
        get_deactive = int(request.query_params.get("deactive",0))
        account_id = int(request.query_params.get("account_id",0))
        
        if not get_private:
            problem = problem.filter(is_private=False)
        if not get_deactive:
            problem = problem.filter(is_active=True)
        if account_id != 0:
            problem = problem.filter(account_id=account_id)

        problem = problem.order_by('-problem_id')

        serialize = ProblemPopulateAccountSerializer(problem,many=True)

        result = [model_to_dict(i) for i in problem]

        for i in result:
            i['creator'] = model_to_dict(Account.objects.get(account_id=i['account']))

        return Response({'problems':serialize.data},status=status.HTTP_200_OK)
    elif request.method == DELETE:
        target = request.data.get("problem",[])
        problems = Problem.objects.filter(problem_id__in=target)
        problems.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view([GET,PUT,DELETE])
def one_problem(request,problem_id: int):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
    except Problem.DoesNotExist:
        return Response({'detail': "Problem doesn't exist!"},status=status.HTTP_404_NOT_FOUND)
    testcases = Testcase.objects.filter(problem_id=problem_id)

    if request.method == GET:
            problem_serialize = ProblemPopulateAccountSerializer(problem)
            testcases_serialize = TestcaseSerializer(testcases,many=True)
            return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_200_OK)
    elif request.method == PUT:
        
        problem.title = request.data.get("title",problem.title)
        problem.language = request.data.get("language",problem.language)
        problem.description = request.data.get("description",problem.description)
        problem.solution = request.data.get("solution",problem.solution)
        problem.time_limit = request.data.get("time_limit",problem.time_limit)  
        problem.is_private = request.data.get("is_private",problem.is_private)

        if 'testcases' in request.data:
            program_output = PythonGrader(problem.solution,request.data['testcases'],1,1.5).generate_output()

            if sum([1 for i in program_output if i.runtime_status != "OK"]) > 0:
                return Response({'detail': 'Error during editing. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)

            testcases.delete()
            testcase_result = []
            for unit in program_output:
                testcase = Testcase(
                    problem = problem,
                    input = unit.input,
                    output = unit.output
                )
                testcase.save()
                testcase_result.append(testcase)
            problem.save()

            problem_serialize = ProblemSerializer(problem)
            testcases_serialize = TestcaseSerializer(testcase_result,many=True)

            return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_201_CREATED)

        problem.save()
        problem_serialize = ProblemSerializer(problem)
        return Response(problem_serialize.data,status=status.HTTP_201_CREATED)

    elif request.method == DELETE:
        problem.delete()
        testcases.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)