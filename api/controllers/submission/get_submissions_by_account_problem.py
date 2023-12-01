from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_submissions_by_account_problem(account_id:int,problem_id:int):
    submissions = Submission.objects.filter(account=account_id,problem=problem_id)

    if submissions.count() == 0:
        return Response({"best_submission": None,"submissions": []},status=status.HTTP_204_NO_CONTENT)

    submissions = submissions.order_by('-submission_id')
    
    best_submission_id = submissions.order_by('-passed_ratio','-submission_id').first().submission_id

    best_submission = None
    result = []
    
    for submission in submissions:
        submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
        submission.runtime_output = submission_testcases
        result.append(submission)

        if submission.submission_id == best_submission_id:
            best_submission = submission
    
    best_submission_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(best_submission)
    submissions_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(result,many=True)

    return Response({"best_submission": best_submission_serializer.data,"submissions": submissions_serializer.data},status=status.HTTP_200_OK)