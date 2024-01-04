from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict

def replace_problems_empty_description(request):
    problems = Problem.objects.all()
    for problem in problems:
        if len(problem.description) == 0:
            problem.description = f'[{{"id": "1","type": "p","children": [{{ "text": "" }}]}}]'
            problem.save()
        elif problem.description[0] != '[':
            problem.description = f'[{{"id": "1","type": "p","children": [{{ "text": "{problem.description}" }}]}}]'
            problem.save()
        elif "ELEMENT_PARAGRAPH" in problem.description:
            problem.description = f'[{{"id": "1","type": "p","children": [{{ "text": "{problem.description}" }}]}}]'
            problem.save()
        problem.description = f'[{{"id": "1","type": "p","children": [{{ "text": "" }}]}}]'
        problem.save()
    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)