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
def create_collections(request,account_id:int):
    request.data['owner'] = account_id

    serialize = CollectionSerializer(data=request.data)

    if serialize.is_valid():
        serialize.save()
        return Response(serialize.data,status=status.HTTP_201_CREATED)
    else:
        return Response(serialize.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view([GET])
def all_collections(request):
    collections = Collection.objects.all()

    account_id = request.query_params.get('account_id',0)

    if account_id:
        collections = collections.filter(owner_id=account_id)

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
        # print()

        populated_collections.append(collection_data)

    return Response({
        'collections': populated_collections
    },status=status.HTTP_200_OK)

@api_view([GET,PUT,DELETE])
def one_collection(request,collection_id:int):
    collection = Collection.objects.get(collection_id=collection_id)
    problems = Problem.objects.filter(collectionproblem__collection_id=collection_id)
    collectionProblems = CollectionProblem.objects.filter(collection=collection)

    if request.method == GET:
        collection_ser = CollectionSerializer(collection)
        
        populated_problems = []
        for col_prob in collectionProblems:
            col_prob_serialize = CollectionProblemSerializer(col_prob)
            prob_serialize = ProblemSerializer(col_prob.problem)
            populated_problems.append({**col_prob_serialize.data,**prob_serialize.data})

        return Response({
            'collection': collection_ser.data,
            'problems': populated_problems
        } ,status=status.HTTP_200_OK)
    
    if request.method == PUT:
        collection_ser = CollectionSerializer(collection,data=request.data,partial=True)
        if collection_ser.is_valid():
            collection_ser.save()
            return Response(collection_ser.data,status=status.HTTP_200_OK)
        else:
            return Response(collection_ser.errors,status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == DELETE:
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view([PUT,DELETE])
def collection_problems(request,collection_id:int):
    collection = Collection.objects.get(collection_id=collection_id)

    if request.method == PUT:
        populated_problems = []

        index = 0
        for problem_id in request.data['problem_ids']:

            problem = Problem.objects.get(problem_id=problem_id)

            alreadyExist = CollectionProblem.objects.filter(problem=problem,collection=collection)
            if alreadyExist:
                alreadyExist.delete()
            
            collection_problem = CollectionProblem(
                problem=problem,
                collection=collection,
                order=index
            )
            print(problem,index)
            collection_problem.save()
            index += 1
            cp_serialize = CollectionProblemSerializer(collection_problem)
            populated_problems.append(cp_serialize.data)
        
        collection_serialize = CollectionSerializer(collection)

        return Response({
            'collection': collection_serialize.data,
            'problems': populated_problems
        },status=status.HTTP_201_CREATED)
    
    if request.method == DELETE:
        CollectionProblem.objects.filter(collection=collection,problem_id__in=request.data['problem_ids']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)