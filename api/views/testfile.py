from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

@api_view([POST])
def upload_testfile(request,problem_id:int):
    # problem = Problem.objects.get(problem_id=problem_id)
    
    testfile_serializes = []
    for testfile in request.FILES.getlist('testfiles'):
        # print(testfile)
        filename = str(testfile)
        print(filename)
        print(type(filename))
        serialize = TestFileSerializer(data={'problem': problem_id,'file':testfile,'filename':str(testfile)})
        if serialize.is_valid():
            serialize.save()
            testfile_serializes.append(serialize.data)
        else:
            print(serialize.errors)
            return Response({'detail': 'Cannot upload file!'},status=status.HTTP_400_BAD_REQUEST)
    return Response({'testfiles': testfile_serializes},status=status.HTTP_201_CREATED)
        
@api_view([DELETE])
def remove_testfile(request,problem_id:int):
    TestFile.objects.filter(problem=problem_id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)