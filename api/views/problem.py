# from ..utility import JSONParser, JSONParserOne, passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict


# Create your views here.
@api_view([POST])
def create_problem(request):
    problem = Problem(
        language = request.data['language'],
        title = request.data['title'],
        description = request.data['description'],
        solution = request.data['solution']
    )
    problem.save()

    for test in request.data['testcases']:
        testcase = Testcase(
            problem_id = problem,
            unit = test
        )
        testcase.save()
    
    return Response({'detail': 'Problem has been created!'},status=status.HTTP_201_CREATED)

@api_view([GET])
def get_problem(request,problem_id: int):
    problem = Problem.objects.get(problem_id=problem_id)
    return Response({'result':model_to_dict(problem)},status=status.HTTP_200_OK)