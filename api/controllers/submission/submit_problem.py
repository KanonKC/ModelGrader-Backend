from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader,Grader,ProgramGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from ...utility import regexMatching
from time import sleep
from ..problem.update_problem_difficulty import *

QUEUE = [0,0,0,0,0,0,0,0,0,0]

def avaliableQueue():
    global QUEUE
    for i in range(len(QUEUE)):
        if QUEUE[i] == 0:
            return i
    return -1

def submit_problem_function(account_id:str,problem_id:str,topic_id:str,request):
    global QUEUE
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem=problem,deprecated=False)
    account = Account.objects.get(account_id=account_id)

    submission_code = request.data['submission_code']
    solution_input = [model_to_dict(i)['input'] for i in testcases]
    solution_output = [model_to_dict(i)['output'] for i in testcases]

    if not regexMatching(problem.submission_regex,submission_code):
        grading_result = '-'*len(solution_input)
    else:
        empty_queue = avaliableQueue()
        while empty_queue == -1:
            empty_queue = avaliableQueue()
            sleep(5)

        QUEUE[empty_queue] = 1
        # grading_result = grader.grading(empty_queue+1,submission_code,solution_input,solution_output)
        grader: ProgramGrader = Grader[request.data['language']]
        grading_result = grader(submission_code,solution_input,empty_queue+1,1.5).grading(solution_output)
        QUEUE[empty_queue] = 0

    total_score = sum([i.is_passed for i in grading_result.data if i.is_passed])
    max_score = len(grading_result.data)

    submission = Submission(
        problem = problem,
        account = account,
        language = request.data['language'],
        submission_code = request.data['submission_code'],
        is_passed = grading_result.is_passed,
        score = total_score,
        max_score = max_score,
        passed_ratio = total_score/max_score
    )

    if topic_id:
        submission.topic = Topic.objects.get(topic_id=topic_id)

    submission.save()

    # Best Submission
    try:
        best_submission = None
        if topic_id:
            best_submission = BestSubmission.objects.get(problem=problem,account=account,topic=Topic.objects.get(topic_id=topic_id))
        else:
            best_submission = BestSubmission.objects.get(problem=problem,account=account)
    except:
        best_submission = BestSubmission(
            problem = problem,
            account = account,
            topic = Topic.objects.get(topic_id=topic_id) if topic_id else None,
            submission = submission
        )
        best_submission.save()        
    else:
        if submission.passed_ratio >= best_submission.submission.passed_ratio:
            best_submission.submission = submission
            best_submission.save()

    # End Best Submission
            
    submission_testcases = []
    for i in range(len(grading_result.data)):
        submission_testcases.append(SubmissionTestcase(
            submission = submission,
            testcase = testcases[i],
            output = grading_result.data[i].output,
            is_passed = grading_result.data[i].is_passed,
            runtime_status = grading_result.data[i].runtime_status
        ))

    SubmissionTestcase.objects.bulk_create(submission_testcases)

    submission.runtime_output = submission_testcases
    testser = SubmissionPopulateSubmissionTestcaseSecureSerializer(submission)

    update_problem_difficulty(problem)

    return Response(testser.data,status=status.HTTP_201_CREATED)

def submit_problem(account_id:str,problem_id:str,request):
    try:
        return submit_problem_function(account_id,problem_id,None,request)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)