from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *

def record_visited_problem(problem:Problem,account:Account):
    visited_log = VisitedLog(problem=problem,account=account)
    visited_log.save()
    return visited_log

def record_visited_collection(collection:Collection,account:Account):
    visited_log = VisitedLog(collection=collection,account=account)
    visited_log.save()
    return visited_log
    
def record_visited_topic(topic:Topic,account:Account):
    visited_log = VisitedLog(topic=topic,account=account)
    visited_log.save()
    return visited_log