from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_group_permissions_collection(collection:Collection,request):

    CollectionGroupPermission.objects.filter(collection=collection).delete()

    print(request.data['groups'])

    collection_group_permissions = []
    for collection_request in request.data['groups']:
        group = Group.objects.get(group_id=collection_request['group_id'])
        collection_group_permissions.append(
            CollectionGroupPermission(
                collection=collection,
                group=group,
                **collection_request
        ))

    CollectionGroupPermission.objects.bulk_create(collection_group_permissions)

    collection.group_permissions = collection_group_permissions
    serialize = CollectionPopulateCollectionGroupPermissionsPopulateGroupSerializer(collection)

    return Response(serialize.data,status=status.HTTP_202_ACCEPTED)