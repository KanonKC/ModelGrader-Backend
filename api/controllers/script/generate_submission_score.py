from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict

def generate_submission_score(request):
    submissions = Submission.objects.all()
    total = len(submissions)
    count = 0
    for submission in submissions:
        submission.score = submission.result.count('P')
        submission.max_score = len(submission.result)
        submission.passed_ratio = submission.score/submission.max_score
        submission.save()
        count += 1
        print(f"({count}/{total})")
    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)