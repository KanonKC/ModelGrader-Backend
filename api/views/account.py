from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

@api_view([GET,POST])
def account_collection(request):
    if request.method == GET:
        accounts = Account.objects.all()
        serialize = AccountSecureSerializer(accounts,many=True)
        return Response({
            "accounts": serialize.data
        },status=status.HTTP_200_OK)
    
    elif request.method == POST:
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
        serialize = AccountSerializer(account)
        return Response(serialize.data,status=status.HTTP_200_OK)
    except:
        return Response({'message':'Account not found!'},status=status.HTTP_404_NOT_FOUND)

@api_view([PUT])
def change_password(request,account_id):
    account = Account.objects.get(account_id=account_id)
    account.password = passwordEncryption(request.data['password'])
    account.save()

    return Response({'message':"Your password has been changed"})

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
    
    return Response({"submissions_by_date": submission_by_date})

# @api_view([GET])
# def get_passed_submission(request,account_id:int):
#     submissions = Submission.objects.filter(account_id=account_id,is_passed=True)

#     serialize = SubmissionSerializer(submissions,many=True)
