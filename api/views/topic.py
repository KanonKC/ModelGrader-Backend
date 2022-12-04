from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem, Submission,Testcase, Topic, TopicProblem
from rest_framework import status
from django.forms.models import model_to_dict

@api_view([POST])
@parser_classes([MultiPartParser,FormParser])
def create_topic(request,account_id :int):
    request.data = dict(request.data)
    account = Account.objects.get(account_id=account_id)
    # request.data.extra(select={'account_id':account})
    request.data['account_id'] = account
    topic = Topic(**request.data)
    topic.save()
    return Response({'topic':model_to_dict(topic)},status=status.HTTP_201_CREATED)

@api_view([GET])
def one_topic(request,topic_id:int):
    topic = Topic.objects.get(topic_id=topic_id)
    topicProblem = Problem.objects.filter(topicproblem__topic_id=topic_id)

    if request.method == GET:
        return Response({
            "topic": model_to_dict(topic),
            "problem": [model_to_dict(i) for i in topicProblem]
        },status=status.HTTP_200_OK)
    elif request.method == PUT:
        topic.name = request.data.get("name",topic.name)
        topic.description = request.data.get("description",topic.description)
        topic.is_active = request.data.get("is_active",topic.is_active)
        topic.is_private = request.data.get("is_private",topic.is_private)
        return Response({
            "topic": model_to_dict(topic)
        },status=status.HTTP_200_OK)

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