from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def populated_problems(collections: Collection):
    problemCollections = CollectionProblem.objects.filter(collection__in=collections)

    populated_collections = []
    for collection in collections:
        collection.problems = problemCollections.filter(collection=collection)
        populated_collections.append(collection)

    return populated_collections

def get_all_collections_by_account(account:Account):

    collections = Collection.objects.filter(creator=account).order_by('-updated_date')
    collections = populated_problems(collections)
    serialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(collections,many=True)

    manageableCollections = Collection.objects.filter(collectiongrouppermission__permission_manage_collections=True,collectiongrouppermission__group__in=GroupMember.objects.filter(account=account).values_list("group",flat=True)).order_by('-updated_date')
    manageableCollections = populated_problems(manageableCollections)
    manageableSerialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(manageableCollections,many=True)

    return Response({
        'collections': serialize.data,
        'manageable_collections': manageableSerialize.data
    },status=status.HTTP_200_OK)