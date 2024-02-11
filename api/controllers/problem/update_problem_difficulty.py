from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from ...difficulty_predictor.preprocess import *
from ...difficulty_predictor.predictor import *

try:
    import pandas as pd
    pd.options.mode.chained_assignment = None
    success = True
except:
    success = False

def update_problem_difficulty(problem:Problem):

    if not success:
        return

    submissions = Submission.objects.filter(problem=problem)

    if submissions.count() < 10:
        return

    # Change them to DataFrame
    df = pd.DataFrame(data={
        'submission_id': [i.submission_id for i in submissions],
        'account_id': [i.account_id for i in submissions],
        'problem_id': [i.problem_id for i in submissions],
        'score': [i.score for i in submissions],
        'max_score': [i.max_score for i in submissions],
        'passed_ratio': [i.passed_ratio for i in submissions],
        'language': [i.language for i in submissions],
        'submission_code': [i.submission_code for i in submissions],
        'date': [i.date for i in submissions],
        'is_passed': [i.is_passed for i in submissions],
    })

    [total_attempt,time_used] = modelgrader_preprocessor(df)
    difficulty = predict(total_attempt,time_used)
    
    problem.difficulty = difficulty
    problem.save()