from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

@api_view([POST])
@parser_classes([MultiPartParser,FormParser])
def create_topic(request,account_id :int):
    request.data._mutable=True
    request.data['account'] = account_id
    serializer = TopicSerializer(data=request.data)
    print(serializer)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view([GET])
def all_topic(request):
    topics = Topic.objects.all()

    account_id = request.query_params.get('account_id',0)

    if account_id:
        topics = topics.filter(account_id=account_id)

    serializer = TopicSerializer(topics,many=True)

    return Response({
        'topics': serializer.data
    },status=status.HTTP_200_OK)

@api_view([GET,PUT,DELETE])
def one_topic(request,topic_id:int):
    topic = Topic.objects.get(topic_id=topic_id)
    topicCollections = TopicCollection.objects.filter(topic_id=topic_id)
    accessedAccounts = Account.objects.filter(topicaccountaccess__topic_id=topic_id)
    
    if request.method == GET:
        topic_ser = TopicSerializer(topic)
        populate_collections = []

        for top_col in topicCollections:
            collection_serialize = CollectionSerializer(top_col.collection)
            collection_data = collection_serialize.data

            populate_problems = []
            collection_problems = CollectionProblem.objects.filter(collection=top_col.collection)
            for col_prob in collection_problems:
                prob_serialize = ProblemSerializer(col_prob.problem)
                col_prob_serialize = CollectionProblemSerializer(col_prob)
                populate_problems.append({**col_prob_serialize.data,**prob_serialize.data})

            collection_data['problems'] = populate_problems
            top_col_serialize = TopicCollectionSerializer(top_col)
            populate_collections.append({**top_col_serialize.data,**collection_data})

        accessedAccountsSerialize = AccountSerializer(accessedAccounts,many=True)

        return Response({
            "topic": topic_ser.data,
            "collections": sorted(populate_collections,key=lambda collection: collection['order']),
            "accessed_accounts": accessedAccountsSerialize.data
        },status=status.HTTP_200_OK)
    elif request.method == PUT:
        topic_ser = TopicSerializer(topic,data=request.data,partial=True)
        if topic_ser.is_valid():
            topic_ser.save()
            return Response(topic_ser.data,status=status.HTTP_200_OK)
        return Response(topic_ser.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == DELETE:
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view([PUT])
def topic_collection(request,topic_id:int,method:str):
    topic = Topic.objects.get(topic_id=topic_id)

    if method == "add":
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
            "topic": TopicSerializer(topic).data,
            "collections": populated_collections
        },status=status.HTTP_201_CREATED)

    elif method == "remove":
        TopicCollection.objects.filter(topic_id=topic_id,collection_id__in=request.data['collection_ids']).delete()
        # collections = Collection.objects.filter(collection_id__in=request.data['collection_ids'])
        # problems = Problem.objects.filter(problem_id__in=request.data['problems_id'])
        # TopicProblem.objects.filter(topic_id=topic,problem_id__in=problems).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view([POST,PUT])
def account_access(request,topic_id:int):
    topic = Topic.objects.get(topic_id=topic_id)
    target_accounts = Account.objects.filter(account_id__in=request.data['account_ids'])

    if request.method == POST:
        accessedAccounts = []
        for account in target_accounts:
            topic_account = TopicAccountAccess(
                topic = topic,
                account = account
            )
            # print(topic_account)
            topic_account.save()
            accessedAccounts.append(topic_account)
            # ta_serialize = TopicAccountAccessSerialize(topic_account)
        
        serialize = TopicAccountAccessSerialize(accessedAccounts,many=True)

        return Response({
            "accounts": serialize.data
        },status=status.HTTP_201_CREATED)
    
    elif request.method == PUT:
        topicAccountAccesses = TopicAccountAccess.objects.filter(account_id__in=request.data['account_ids'])
        topicAccountAccesses.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
