from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_problems_to_collection(collection:Collection,request):
    CollectionProblem.objects.filter(collection=collection).delete()

    collection_problems = []
    order = 0
    for problem_id in request.data['problem_ids']:
        problem = Problem.objects.get(problem_id=problem_id)
        collection_problem = CollectionProblem(
            problem=problem,
            collection=collection,
            order=order
        )
        collection_problems.append(collection_problem)
        order += 1

    CollectionProblem.objects.bulk_create(collection_problems)
    collection.updated_date = timezone.now()
    collection.save()
    problem_serialize = CollectionProblemPopulateProblemSecureSerializer(collection_problems,many=True)
    collection_serialize = CollectionSerializer(collection)

    return Response({
        **collection_serialize.data,
        'problems': problem_serialize.data
    },status=status.HTTP_201_CREATED)