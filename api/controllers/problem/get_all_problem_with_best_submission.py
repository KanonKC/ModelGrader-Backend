from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_problem_with_best_submission(account_id:int):
    problems = Problem.objects.all().order_by('-updated_date')
    
    pass

    
    # return Response({"problems":problem_ser.data},status=status.HTTP_200_OK)