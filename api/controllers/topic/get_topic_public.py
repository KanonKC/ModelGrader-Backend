from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_topic_public(topic_id:str,request):

    account_id = request.query_params.get('account_id',None)

    topic = Topic.objects.get(topic_id=topic_id)
    account = Account.objects.get(account_id=account_id)
    topicCollections = TopicCollection.objects.filter(topic=topic)

    for tp in topicCollections:
        # tp.collection.problems = CollectionProblem.objects.filter(collection=tp.collection)
        collectionProblems = CollectionProblem.objects.filter(collection=tp.collection)
        for cp in collectionProblems:
            try:
                best_submission = BestSubmission.objects.get(problem=cp.problem,account=account,topic=topic)
                best_submission = best_submission.submission
                best_submission.runtime_output = SubmissionTestcase.objects.filter(submission=best_submission)
            except:
                best_submission = None
            cp.problem.best_submission = best_submission

        tp.collection.problems = collectionProblems

    topic.collections = topicCollections

    serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(topic)

    return Response(serialize.data,status=status.HTTP_200_OK)
