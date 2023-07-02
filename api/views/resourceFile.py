from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

@api_view([GET,POST,PUT])
def manage_resource(request,account_id:int):
    if request.method == GET:
        resources = ResourceFile.objects.filter(owner_id=account_id)
        serializer = ResourceFileSerializer(resources,many=True)
        return Response({'resources': serializer.data},status=status.HTTP_200_OK)
    if request.method == POST:
        testfile_serializes = []
        for resourceFile in request.FILES.getlist('resources'):
            serialize = ResourceFileSerializer(data={'owner': account_id,'file':resourceFile})
            if serialize.is_valid():
                serialize.save()
                testfile_serializes.append(serialize.data)
            else:
                print(serialize.errors)
                return Response({'detail': 'Cannot upload file!'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'resources': testfile_serializes},status=status.HTTP_201_CREATED)
    if request.method == PUT:
        ResourceFile.objects.filter(resource_id__in=request.data['resource_id']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)