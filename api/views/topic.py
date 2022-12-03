from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem, Submission,Testcase, Topic, TopicProblem
from rest_framework import status
from django.forms.models import model_to_dict

@api_view([POST])
def create_topic(request,account_id :int):
    account = Account.objects.get(account_id=account_id)
    request.data['topic']['account_id'] = account
    topic = Topic(**request.data['topic'])

    topic.save()

    populated_problem = []
    for id in request.data['problems']:
        problem = Problem.objects.get(problem_id=id)
        topicProblem = TopicProblem(
            topic_id=topic,
            problem_id=problem
        )    
        topicProblem.save()
        populated_problem.append(model_to_dict(problem))

    return Response({'topic':model_to_dict(topic),'problem':populated_problem},status=status.HTTP_201_CREATED)

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
        pass
