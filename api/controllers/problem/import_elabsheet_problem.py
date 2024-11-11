from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def import_elabsheet_problem(request, problem: Problem):
    print("importing elabsheet problem")
    print(request.data)
    # Get file
    file = request.data.get('file')
    problem.pdf_url = file
    print(file)
    print(problem.pdf_url)
    return Response(status=status.HTTP_204_NO_CONTENT)