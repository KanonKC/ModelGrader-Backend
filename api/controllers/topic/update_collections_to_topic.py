from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_collections_to_topic(topic:Topic,request):
    TopicCollection.objects.filter(topic=topic).delete()

    topic_collections = []
    order = 0
    for collection_id in request.data['collection_ids']:
        collection = Collection.objects.get(collection_id=collection_id)
        topic_collection = TopicCollection(
            collection=collection,
            topic=topic,
            order=order
        )
        topic_collections.append(topic_collection)
        order += 1

    TopicCollection.objects.bulk_create(topic_collections)
    topic.updated_date = timezone.now()
    topic.save()

    collection_serialize = TopicCollectionPopulateCollectionSerializer(topic_collections,many=True)
    topic_serialize = TopicSerializer(topic)

    return Response({
        **topic_serialize.data,
        'collections': collection_serialize.data
    },status=status.HTTP_201_CREATED)