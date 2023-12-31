from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_collections_by_account(account_id:str):
    collections = Collection.objects.filter(creator=account_id).order_by('-updated_date')
    problemCollections = CollectionProblem.objects.filter(collection__in=collections)

    populated_collections = []
    for collection in collections:
        con_probs = problemCollections.filter(collection=collection)
        serialize = CollectionSerializer(collection)
        collection_data = serialize.data
        collection_data['problems'] = CollectionProblemPopulateProblemSecureSerializer(con_probs,many=True).data

        populated_collections.append(collection_data)

    return Response({
        'collections': populated_collections
    },status=status.HTTP_200_OK)