from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from django.utils import timezone

def update_problem(problem_id:str,request):
    try:
        problem = Problem.objects.get(problem_id=problem_id)
    except Problem.DoesNotExist:
        return Response({'detail': "Problem doesn't exist!"},status=status.HTTP_404_NOT_FOUND)
    testcases = Testcase.objects.filter(problem_id=problem_id,deprecated=False)

    print("AAA")

    problem.title = request.data.get("title",problem.title)
    problem.language = request.data.get("language",problem.language)
    problem.description = request.data.get("description",problem.description)
    problem.solution = request.data.get("solution",problem.solution)
    problem.time_limit = request.data.get("time_limit",problem.time_limit)  
    problem.is_private = request.data.get("is_private",problem.is_private)

    problem.updated_date = timezone.now()

    print("BBB")

    if 'testcases' in request.data:
        running_result = PythonGrader(problem.solution,request.data['testcases'],1,1.5).generate_output()

        # if not running_result.runnable:
        #     return Response({'detail': 'Error during editing. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)
        print("ZZZZZ")
        for testcase in testcases:
            testcase.deprecated = True
            testcase.save()
        print("ZZZZZ")
        testcase_result = []
        for unit in running_result.data:
            print("YYYYY")
            testcase2 = Testcase(
                problem = problem,
                input = unit.input,
                output = unit.output,
                runtime_status = unit.runtime_status
            )
            print("YYYYY",testcase2.testcase_id)
            testcase2.save()
            print("YYYYY")
            testcase_result.append(testcase2)
        problem.save()
        print("ZZZZZ")
        problem_serialize = ProblemSerializer(problem)
        testcases_serialize = TestcaseSerializer(testcase_result,many=True)

        return Response({**problem_serialize.data,'testcases': testcases_serialize.data},status=status.HTTP_201_CREATED)
    
    if 'solution' in request.data:
        testcases = Testcase.objects.filter(problem_id=problem_id,deprecated=False)
        program_input = [i.input for i in testcases]
        running_result = PythonGrader(problem.solution,program_input,1,1.5).generate_output()

        if not running_result.runnable:
            return Response({'detail': 'Error during editing. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)

    print("CCC")
    problem.save()
    problem_serialize = ProblemSerializer(problem)
    return Response(problem_serialize.data,status=status.HTTP_201_CREATED)
