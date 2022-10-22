from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import Problem, Submission,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..sandbox import grader

@api_view([POST])
def submit_problem(request,problem_id):
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem_id=problem_id)

    submission_code = request.data['submission_code']
    solution_input = [model_to_dict(i)['input'] for i in testcases]
    solution_output = [model_to_dict(i)['output'] for i in testcases]

    grading_result = grader.grading(submission_code,solution_input,solution_output)

    submission = Submission(
        problem_id = problem,
        submission_code = request.data['submission_code'],
        result = grading_result
    )
    submission.save()

    return Response(model_to_dict(submission),status=status.HTTP_201_CREATED)

@api_view([GET])
def view_all_submission(request):
    submission = Submission.objects.all()
    problem_id = request.query_params.get("problem_id", 0)
    passed = request.query_params.get("passed", -1)
    if problem_id:
        submission = submission.filter(problem_id=problem_id)
    
    result = [model_to_dict(i) for i in submission]

    if int(passed) == 0:
        print("Here")
        result = [i for i in result if 'E' in i['result'] or '-' in i['result']]
    elif int(passed) == 1:
        result = [i for i in result if 'E' not in i['result'] and '-' not in i['result']]
    return Response({'count':len(result),'result':result},status=status.HTTP_200_OK)