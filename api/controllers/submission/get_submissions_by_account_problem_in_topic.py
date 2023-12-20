from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_submissions_by_account_problem_in_topic(account_id:int,problem_id:int,topic_id:int):
    submissions = Submission.objects.filter(account=account_id,problem=problem_id,topic_id=topic_id)

    if submissions.count() == 0:
        return Response({"best_submission": None,"submissions": []},status=status.HTTP_204_NO_CONTENT)

    submissions = submissions.order_by('-submission_id')
    
    result = []
    
    for submission in submissions:
        submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
        submission.runtime_output = submission_testcases
        result.append(submission)
    
    best_submission = BestSubmission.objects.filter(problem=problem_id,topic=topic_id,account=account_id).first()
    if best_submission:
        best_submission.submission.runtime_output = SubmissionTestcase.objects.filter(submission=best_submission.submission)
        best_submission_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(best_submission.submission)
        best_submission_result = best_submission_serializer.data
    else:
        best_submission_result = None

    submissions_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(result,many=True)

    return Response({"best_submission": best_submission_result,"submissions": submissions_serializer.data},status=status.HTTP_200_OK)