from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_problem_with_best_submission(account_id:str):

    problems = Problem.objects.all().order_by('-updated_date')

    for problem in problems:
        best_submission = Submission.objects.filter(problem=problem).order_by('-passed_ratio','-submission_id').first()
        print(problem.problem_id,problem.title)
        if not (best_submission is None):
            testcases = SubmissionTestcase.objects.filter(submission=best_submission)
            print(testcases)
            best_submission.runtime_output = testcases
            problem.best_submission = best_submission
        else:
            problem.best_submission = None
    
    problem_ser = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problems,many=True)
    return Response({"problems":problem_ser.data},status=status.HTTP_200_OK)

    
    # return Response({"problems":problem_ser.data},status=status.HTTP_200_OK)