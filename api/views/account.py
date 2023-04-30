from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import SubmissionSerializer

@api_view([POST])
def create_account(request):
    request.data['password'] = passwordEncryption(request.data['password'])
    try:
        account = Account.objects.create(**request.data)
    except Exception as e:
        return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Registration Completed','account':model_to_dict(account)},status=status.HTTP_201_CREATED)

@api_view([GET])
def get_account(request,account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        return Response(model_to_dict(account),status=status.HTTP_200_OK)
    except:
        return Response({'message':'Account not found!'},status=status.HTTP_404_NOT_FOUND)

@api_view([GET])
def get_daily_submission(request,account_id:int):
    submissions = Submission.objects.filter(account_id=account_id)
    serializes = SubmissionSerializer(submissions,many=True)

    submission_by_date = {}

    for submission in serializes.data:
        [date,time] = submission['date'].split("T")
        if date in submission_by_date:
            submission_by_date[date]["submissions"].append(submission)
            submission_by_date[date]["count"] += 1
        else:
            submission_by_date[date] = {"count":1, "submissions": [ submission ]}
    
    print(submission_by_date)

    return Response({"submissions_by_date": submission_by_date})