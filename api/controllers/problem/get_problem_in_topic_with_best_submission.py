from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_problem_in_topic_with_best_submission(account_id:str,topic_id:str,problem:int):

    account = Account.objects.get(account_id=account_id)
    problem = Problem.objects.get(problem_id=problem)
    topic = Topic.objects.get(topic_id=topic_id)

    best_submission = BestSubmission.objects.filter(problem=problem,topic=topic,account=account).first()
    # print(problem.problem_id,problem.title)
    if not (best_submission is None):
        testcases = SubmissionTestcase.objects.filter(submission=best_submission.submission)
        print(testcases)
        best_submission.runtime_output = testcases
        problem.best_submission = best_submission
    else:
        problem.best_submission = None
    
    serialize = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problem)
    return Response(serialize.data,status=status.HTTP_200_OK)

    
    # return Response({"problems":problem_ser.data},status=status.HTTP_200_OK)