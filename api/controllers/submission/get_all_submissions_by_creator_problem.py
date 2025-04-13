from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_submissions_by_creator_problem(problem:Problem, request):

    start = int(request.query_params.get("start",0))
    end = int(request.query_params.get("end",-1))
    # query = request.query_params.get("query","")
    if end == -1: end = None

    submissions = Submission.objects.filter(problem=problem)
    total = submissions.count()


    if submissions.count() == 0:
        return Response({"submissions": []},status=status.HTTP_204_NO_CONTENT)

    submissions = submissions.order_by('-date')
    submissions = submissions[start:end]
    
    result = []
    
    for submission in submissions:
        submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
        submission.runtime_output = submission_testcases
        result.append(submission)

    submissions_serializer = SubmissionPopulateSubmissionTestcaseAndAccountSerializer(result,many=True)

    return Response({
        "submissions": submissions_serializer.data,
        "start": start,
        "end": end,
        "total": total,
    },status=status.HTTP_200_OK)