from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict

def generate_failed_submission_status(request):
    submissionTestcases = SubmissionTestcase.objects.all()

    total = len(submissionTestcases)
    count = 0
    for testcase in submissionTestcases:
        if testcase.runtime_status == "OK" and (not testcase.is_passed):
            testcase.runtime_status = "FAILED"
            testcase.save()
        count += 1
    
        print(f"({count}/{total})")
    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)
