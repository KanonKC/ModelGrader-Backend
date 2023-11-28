from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def add_collections_to_topic(topic_id:int,request):
    topic = Topic.objects.get(topic_id=topic_id)
    populated_collections = []
        
    index = 0
    for collection_id in request.data['collection_ids']:
        collection = Collection.objects.get(collection_id=collection_id)

        alreadyExist = TopicCollection.objects.filter(topic_id=topic.topic_id,collection_id=collection.collection_id)
        if alreadyExist:
            alreadyExist.delete()
            
        topicCollection = TopicCollection(
            topic=topic,
            collection=collection,
            order=index
        )
        topicCollection.save()
        index += 1
        tc_serialize = TopicCollectionSerializer(topicCollection)
        populated_collections.append(tc_serialize.data)
    
    return Response({
        **TopicSerializer(topic).data,
        "collections": populated_collections
    },status=status.HTTP_201_CREATED)
