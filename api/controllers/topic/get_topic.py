from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_topic(topic:Topic):
    topic.group_permissions = TopicGroupPermission.objects.filter(topic=topic)
    
    topic.collections = TopicCollection.objects.filter(topic=topic).order_by('order')

    for tp in topic.collections:
        tp.collection.problems = CollectionProblem.objects.filter(collection=tp.collection)
        tp.collection.group_permissions = CollectionGroupPermission.objects.filter(collection=tp.collection)

    serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupAndTopicGroupPermissionPopulateGroupSerializer(topic)
    
    return Response(serialize.data,status=status.HTTP_200_OK)
    


    # topic = Topic.objects.get(topic_id=topic_id)
    # topicCollections = TopicCollection.objects.filter(topic_id=topic_id)
    # # accessedAccounts = Account.objects.filter(topicaccountaccess__topic_id=topic_id)
    
    # topic_ser = TopicSerializer(topic)
    # populate_collections = []

    # for top_col in topicCollections:
    #     collection_serialize = CollectionSerializer(top_col.collection)
    #     collection_data = collection_serialize.data

    #     populate_problems = []
    #     collection_problems = CollectionProblem.objects.filter(collection=top_col.collection)
    #     for col_prob in collection_problems:
    #         prob_serialize = ProblemSerializer(col_prob.problem)
    #         col_prob_serialize = CollectionProblemSerializer(col_prob)
    #         populate_problems.append({**col_prob_serialize.data,**prob_serialize.data})

    #     collection_data['problems'] = populate_problems
    #     top_col_serialize = TopicCollectionSerializer(top_col)
    #     populate_collections.append({**top_col_serialize.data,**collection_data})

    # # accessedAccountsSerialize = AccountSecureSerializer(accessedAccounts,many=True)

    # return Response({
    #     **topic_ser.data,
    #     "collections": sorted(populate_collections,key=lambda collection: collection['order']),
    #     # "accessed_accounts": accessedAccountsSerialize.data
    # },status=status.HTTP_200_OK)