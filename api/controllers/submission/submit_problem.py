from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from ...utility import regexMatching
from time import sleep

QUEUE = [0,0,0,0,0,0,0,0,0,0]

def avaliableQueue():
    global QUEUE
    for i in range(len(QUEUE)):
        if QUEUE[i] == 0:
            return i
    return -1

def submit_problem(problem_id:int,account_id:int,request):
    global QUEUE
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem=problem)

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
        grading_result = PythonGrader(submission_code,solution_input,empty_queue+1,1.5).grading(solution_output)
        QUEUE[empty_queue] = 0

    total_score = sum([i.is_passed for i in grading_result.data if i.is_passed])
    max_score = len(grading_result.data)

    submission = Submission(
        problem = problem,
        account = Account.objects.get(account_id=account_id),
        submission_code = request.data['submission_code'],
        is_passed = grading_result.is_passed,
        score = total_score,
        max_score = max_score,
        passed_ratio = total_score/max_score
    )
    submission.save()

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

    submission_serialize = SubmissionPoplulateProblemSecureSerializer(submission)
    testcases_serialize = SubmissionTestcaseSecureSerializer(submission_testcases,many=True)

    return Response({
        **submission_serialize.data,
        "runtime_output": testcases_serialize.data
    },status=status.HTTP_201_CREATED)