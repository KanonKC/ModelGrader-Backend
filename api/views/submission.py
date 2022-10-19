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

    candidate = request.data['submission_code']
    solution = model_to_dict(problem)['solution']
    testcases = [model_to_dict(i)['unit'] for i in testcases]

    grading_result = grader.grading(candidate,solution,testcases)

    submission = Submission(
        problem_id = problem,
        submission_code = request.data['submission_code'],
        result = grading_result
    )
    submission.save()

    return Response(model_to_dict(submission),status=status.HTTP_201_CREATED)