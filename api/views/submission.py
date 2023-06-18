from statistics import mode
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.serializers import SubmissionPoplulateProblemSerializer
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem, Submission,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from ..sandbox import grader
from time import sleep

QUEUE = [0,0,0,0,0,0,0,0,0,0]

def avaliableQueue():
    global QUEUE
    for i in range(len(QUEUE)):
        if QUEUE[i] == 0:
            return i
    return -1

@api_view([POST])
def submit_problem(request,problem_id,account_id):
    global QUEUE
    problem = Problem.objects.get(problem_id=problem_id)
    testcases = Testcase.objects.filter(problem=problem)

    submission_code = request.data['submission_code']
    solution_input = [model_to_dict(i)['input'] for i in testcases]
    solution_output = [model_to_dict(i)['output'] for i in testcases]

    empty_queue = avaliableQueue()
    while empty_queue == -1:
        empty_queue = avaliableQueue()
        sleep(5)
    QUEUE[empty_queue] = 1
    grading_result = grader.grading(empty_queue+1,submission_code,solution_input,solution_output)
    QUEUE[empty_queue] = 0

    if '-' in grading_result or 'E' in grading_result or 'T' in grading_result:
        is_passed = False
    else:
        is_passed = True

    submission = Submission(
        problem = problem,
        account = Account.objects.get(account_id=account_id),
        submission_code = request.data['submission_code'],
        result = grading_result,
        is_passed = is_passed,
        score = grading_result.count('P'),
        max_score = len(grading_result),
        passed_ratio = grading_result.count('P')/len(grading_result)
    )
    submission.save()

    return Response(model_to_dict(submission),status=status.HTTP_201_CREATED)

@api_view([GET])
def view_all_submission(request):
    submission = Submission.objects.all()
    
    problem_id = int(request.query_params.get("problem_id", 0))
    account_id = int(request.query_params.get("account_id", 0))
    passed = int(request.query_params.get("passed", -1))
    sort_score = int(request.query_params.get("sort_score", 0))
    sort_date = int(request.query_params.get("sort_date", 0))

    if problem_id != 0:
        submission = submission.filter(problem_id=problem_id)
    if account_id != 0:
        submission = submission.filter(account_id=account_id)

    if passed == 0:
        submission = submission.filter(is_passed=False)
    elif passed == 1:
        submission = submission.filter(is_passed=True)

    if sort_score == -1:
        submission = submission.order_by('passed_ratio')
    elif sort_score == 1:
        submission = submission.order_by('-passed_ratio')

    if sort_date == -1:
        submission = submission.order_by('date')
    elif sort_date == 1:
        submission = submission.order_by('-date') 
        
    # result = [model_to_dict(i) for i in submission]
    serialize = SubmissionPoplulateProblemSerializer(submission,many=True)
    return Response({"result": serialize.data},status=status.HTTP_200_OK)
    # result = serialize.data

    # print(result[0])

    # for row in result:
    #     count = 0
    #     for j in row.get('result'):
    #         if j == 'P':
    #             count += 1
    #     row['score'] = count

    # if passed == 0:
    #     result = [i for i in result if not i['is_passed']]
    # elif passed == 1:
    #     result = [i for i in result if i['is_passed']]

    # if sort_score == -1:
    #     result.sort(key=lambda value: value['score'])
    # if sort_score == 1:
    #     result.sort(key=lambda value: value['score'],reverse=True)
    
    # result = [{'problem': model_to_dict(Problem.objects.get(problem_id=i['problem'])),**i} for i in result]
    # return Response({'count':len(result),'result':result},status=status.HTTP_200_OK)