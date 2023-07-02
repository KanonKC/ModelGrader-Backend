# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from api.sandbox.grader import grading, checker
# from ..constant import GET,POST,PUT,DELETE
# from ..models import Account, Problem,Testcase
# from rest_framework import status
# from django.forms.models import model_to_dict
# from ..serializers import *

# @api_view([POST])
# def upload_resource(request,account_id:int):
#     testfile_serializes = []
#     for resource in request.FILES.getlist('resource'):
#         serialize = TestFileSerializer(data={account_id,'file':resource})
#         if serialize.is_valid():
#             serialize.save()
#             testfile_serializes.append(serialize.data)
#         else:
#             return Response({'detail': 'Error during creating. Your code may has an error/timeout!'},status=status.HTTP_406_NOT_ACCEPTABLE)
#     return Response({**problem_serialize.data,'testfile': testfile_serializes},status=status.HTTP_201_CREATED)
