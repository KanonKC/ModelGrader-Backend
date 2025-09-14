from django.forms.models import model_to_dict
from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from rest_framework import status
from ..serializers import *
from django.db.models import Q
from ..errors.common import *

def create_account(request):
    request.data['password'] = passwordEncryption(request.data['password'])
    try:
        account = Account.objects.create(**request.data)
    except Exception as e:
        raise InternalServerError(e)
    serialize = AccountSerializer(account)
    return serialize.data

def get_account(account_id: str):
    try:
        account = Account.objects.get(account_id=account_id)
        serialize = AccountSerializer(account)
        return serialize.data
    except Account.DoesNotExist:
        raise ItemNotFoundError("Account")

def get_all_accounts(request):
    # get search query
    search = request.GET.get('search', '')
    
    accounts = Account.objects.all()
    
    if search != '':
        accounts = accounts.filter(
            Q(username__icontains=search) | Q(account_id__icontains=search) | Q(email__icontains=search)
        ).distinct()
    
    serialize = AccountSecureSerializer(accounts, many=True)
    return {
        "accounts": serialize.data
    }

def get_daily_submission(account_id:str):
    submissions = Submission.objects.filter(account_id=account_id)
    serializes = SubmissionSerializer(submissions,many=True)

    submission_by_date = {}

    for submission in serializes.data:
        [date,] = submission['date'].split("T")
        if date in submission_by_date:
            submission_by_date[date]["submissions"].append(submission)
            submission_by_date[date]["count"] += 1
        else:
            submission_by_date[date] = {"count":1, "submissions": [ submission ]}
    
    return Response({"submissions_by_date": submission_by_date})