from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_collections(request):
    collections = Collection.objects.all()

    account_id = request.query_params.get('account_id',0)

    if account_id:
        collections = collections.filter(creator_id=account_id)

    populated_collections = []
    for collection in collections:
        con_probs = CollectionProblem.objects.filter(collection=collection)

        populated_cp = []
        for cp in con_probs:
            prob_serialize = ProblemSerializer(cp.problem)
            cp_serialize = CollectionProblemSerializer(cp)
            populated_cp.append({**cp_serialize.data,**prob_serialize.data})
    
        serialize = CollectionSerializer(collection)
        collection_data = serialize.data
        collection_data['problems'] = populated_cp

        populated_collections.append(collection_data)

    return Response({
        'collections': populated_collections
    },status=status.HTTP_200_OK)