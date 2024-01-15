from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_submissions_by_creator_problem(problem:Problem):
    submissions = Submission.objects.filter(problem=problem)

    if submissions.count() == 0:
        return Response({"submissions": []},status=status.HTTP_204_NO_CONTENT)

    submissions = submissions.order_by('-date')
    
    result = []
    
    for submission in submissions:
        submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
        submission.runtime_output = submission_testcases
        result.append(submission)

    submissions_serializer = SubmissionPopulateSubmissionTestcaseAndAccountSerializer(result,many=True)

    return Response({"submissions": submissions_serializer.data},status=status.HTTP_200_OK)