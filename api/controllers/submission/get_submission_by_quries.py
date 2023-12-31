from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_submission_by_quries(request):
    submissions = Submission.objects.all()
    
    # Query params
    problem_id = str(request.query_params.get("problem_id", ""))
    account_id = str(request.query_params.get("account_id", ""))
    topic_id = str(request.query_params.get("topic_id", ""))
    passed = int(request.query_params.get("passed", -1))
    sort_score = int(request.query_params.get("sort_score", 0))
    sort_date = int(request.query_params.get("sort_date", 0))
    start = int(request.query_params.get("start", -1))
    end = int(request.query_params.get("end", -1))

    if problem_id != "":
        submissions = submissions.filter(problem_id=problem_id)
    if account_id != "":
        submissions = submissions.filter(account_id=account_id)
    if topic_id != "":
        submissions = submissions.filter(problem__topic_id=topic_id)

    if passed == 0:
        submissions = submissions.filter(is_passed=False)
    elif passed == 1:
        submissions = submissions.filter(is_passed=True)

    if sort_score == -1:
        submissions = submissions.order_by('passed_ratio')
    elif sort_score == 1:
        submissions = submissions.order_by('-passed_ratio')

    if sort_date == -1:
        submissions = submissions.order_by('date')
    elif sort_date == 1:
        submissions = submissions.order_by('-date')

    if start != -1 and end != -1:
        submissions = submissions[start:end]

    for submission in submissions:
        submission.runtime_output = SubmissionTestcase.objects.filter(submission=submission)
        
    serialize = SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(submissions,many=True)
    return Response({"submissions": serialize.data},status=status.HTTP_200_OK)
