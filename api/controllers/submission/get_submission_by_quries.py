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
    submission = Submission.objects.all()
    
    # Query params
    problem_id = int(request.query_params.get("problem_id", 0))
    account_id = int(request.query_params.get("account_id", 0))
    topic_id = int(request.query_params.get("topic_id", 0))
    passed = int(request.query_params.get("passed", -1))
    sort_score = int(request.query_params.get("sort_score", 0))
    sort_date = int(request.query_params.get("sort_date", 0))

    if problem_id != 0:
        submission = submission.filter(problem_id=problem_id)
    if account_id != 0:
        submission = submission.filter(account_id=account_id)
    if topic_id != 0:
        submission = submission.filter(problem__topic_id=topic_id)

    if passed == 0:
        submission = submission.filter(is_passed=False)
    elif passed == 1:
        submission = submission.filter(is_passed=True)

    if sort_score == -1:
        submission = submission.order_by('passed_ratio')
    elif sort_score == 1:
        submission = submission.order_by('-passed_ratio')

    if sort_date == -1:
        submission = submission.order_by('date')
    elif sort_date == 1:
        submission = submission.order_by('-date') 
        
    serialize = SubmissionPoplulateProblemSerializer(submission,many=True)
    return Response({"submissions": serialize.data},status=status.HTTP_200_OK)
