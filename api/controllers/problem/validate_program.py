from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import Grader,ProgramGrader,RuntimeResultList
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def validate_program(request):
    grader:ProgramGrader = Grader[request.data['language']]
    result:RuntimeResultList = grader(request.data['source_code'],request.data['testcases'],1,request.data['time_limited']).generate_output()

    print(result.getResult())
    print(result.runnable)

    return Response({
        'runnable': result.runnable,
        'has_error': result.has_error,
        'has_timeout': result.has_timeout,
        'runtime_results': result.getResult(),
    },status=status.HTTP_200_OK)