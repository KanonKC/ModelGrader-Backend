from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *
from ..controllers.account.create_account import *
from ..controllers.account.get_account import *
from ..controllers.account.get_all_accounts import *

@api_view([GET,POST])
def all_accounts_view(request):
    if request.method == GET:
        return get_all_accounts(request)
    elif request.method == POST:
        return create_account(request)

@api_view([GET])
def one_creator_view(request,account_id):
    return get_account(account_id)

@api_view([PUT])
def change_password(request,account_id):
    account = Account.objects.get(account_id=account_id)
    account.password = passwordEncryption(request.data['password'])
    account.save()

    return Response({'message':"Your password has been changed"})

@api_view([GET])
def get_daily_submission(request,account_id:str):
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
    
    return Response({"submissions_by_date": submission_by_date})

