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

    result = []
    for submission in submissions:
        submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
        
        serializer = SubmissionSerializer(submission)
        submission_testcases_serializer = SubmissionTestcaseSecureSerializer(submission_testcases,many=True)

        result.append({**serializer.data,"testcases":submission_testcases_serializer.data})

    return Response({"submissions": result},status=status.HTTP_200_OK)