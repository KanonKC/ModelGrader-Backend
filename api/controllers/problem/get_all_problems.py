from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_problems(request):
    problem = Problem.objects.all()

    get_private = int(request.query_params.get("private",0))
    get_deactive = int(request.query_params.get("deactive",0))
    account_id = int(request.query_params.get("account_id",0))
    
    if not get_private:
        problem = problem.filter(is_private=False)
    if not get_deactive:
        problem = problem.filter(is_active=True)
    if account_id != 0:
        problem = problem.filter(creator_id=account_id)

    problem = problem.order_by('-problem_id')

    serialize = ProblemPopulateAccountSerializer(problem,many=True)

    return Response({'problems':serialize.data},status=status.HTTP_200_OK)
   