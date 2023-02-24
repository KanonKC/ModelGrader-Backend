from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem, Submission,Testcase, Topic, TopicProblem
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import TopicSerializer,TopicProblemSerializer,ProblemSerializer

@api_view([POST])
def create_topic(request,account_id :int):
    account = Account.objects.get(account_id=account_id)
    request.data['account_id'] = account.account_id
    serializer  = TopicSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(account_id=account)
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
    topicProblem = Problem.objects.filter(topicproblem__topic_id=topic_id)

    if request.method == GET:
        topic_ser = TopicSerializer(topic)
        problem_ser = ProblemSerializer(topicProblem,many=True)
        return Response({
            "topic": topic_ser.data,
            "problem": problem_ser.data
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

@api_view([PUT,DELETE])
def topic_problem(request,topic_id:int):
    topic = Topic.objects.get(topic_id=topic_id)

    if request.method == PUT:
        populated_problem = []
        for id in request.data['problems_id']:
            problem = Problem.objects.get(problem_id=id)
            if TopicProblem.objects.filter(topic_id=topic,problem_id=problem):
                continue
            topicProblem = TopicProblem(
                topic_id=topic,
                problem_id=problem
            )    
            topicProblem.save()
            populated_problem.append(model_to_dict(problem))
        return Response({
            "topic": model_to_dict(topic),
            "problems": populated_problem
        },status=status.HTTP_201_CREATED)

    elif request.method == DELETE:
        problems = Problem.objects.filter(problem_id__in=request.data['problems_id'])
        TopicProblem.objects.filter(topic_id=topic,problem_id__in=problems).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)