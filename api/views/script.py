from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *
from ..controllers.script.generate_submission_score import generate_submission_score
from ..difficulty_predictor.preprocess import *
from ..difficulty_predictor.predictor import *
from ..controllers.problem.update_problem_difficulty import update_problem_difficulty

# @api_view([POST])
# def run_script(request):
#     submissions = Submission.objects.all()
#     total = len(submissions)
#     count = 0
#     for submission in submissions:
#         submission.score = submission.result.count('P')
#         submission.max_score = len(submission.result)
#         submission.passed_ratio = submission.score/submission.max_score
#         submission.save()
#         count += 1
#         print(f"({count}/{total})")
#     return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)

# @api_view([POST])
# def run_script(request):
#     submissionTestcases = SubmissionTestcase.objects.all()

#     total = len(submissionTestcases)
#     count = 0
#     for testcase in submissionTestcases:
#         if testcase.runtime_status == "OK" and (not testcase.is_passed):
#             testcase.runtime_status = "FAILED"
#             testcase.save()
#         count += 1
    
#         print(f"({count}/{total})")
#     return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)

# @api_view([POST])
# def run_script(request):
#     topics = Topic.objects.all()
#     for topic in topics:
#         if len(topic.description) == 0:
#             topic.description = f'[{{"id": "1","type": ELEMENT_PARAGRAPH,"children": [{{ "text": "" }}]}}]'
#             topic.save()
#         elif topic.description[0] != '[':
#             topic.description = f'[{{"id": "1","type": ELEMENT_PARAGRAPH,"children": [{{ "text": "{topic.description}" }}]}}]'
#             topic.save()
#     return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)

# @api_view([POST])
# def run_script(request):
#     # collections = Collection.objects.all()
#     # for collection in collections:
#     #     collection.description = '[{"id":"1","type":"p","children":[{"text":"Just course"}]}]'
#     #     collection.save()
#     # generate_submission_score(request)
#     problems = Problem.objects.all()
#     for problem in problems:
#         problem.allowed_languages = "python,c,cpp"
#         problem.save()
#     return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)

# @api_view([POST])
# def run_script(request):
#     problems = Problem.objects.all()
#     for problem in problems:
#         update_problem_difficulty(problem)

#     return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)

@api_view([POST])
def run_script(request):
    problems = Problem.objects.all()
    for problem in problems:
        if problem.language == "py":
            problem.language = "python"
            problem.save()

    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)
