from time import sleep
from api.services.problem.problem_service import ProblemService
from api.services.problem.serializers import ProblemPopulateTestcaseSerializer
from api.utility import regexMatching
from api.sandbox.grader import Grader, ProgramGrader
from ...models import *
from django.forms.models import model_to_dict
from .serializers import *
from ...errors.common import *

class SubmissionService:

    def __init__(self):
        self.problem_service = ProblemService()

    def get_all_submissions_by_creator_problem(self, problem:Problem, request):
        start = int(request.query_params.get("start",0))
        end = int(request.query_params.get("end",-1))
        # query = request.query_params.get("query","")
        if end == -1: end = None

        submissions = Submission.objects.filter(problem=problem)
        total = submissions.count()

        if submissions.count() == 0:
            return {"submissions": []}

        submissions = submissions.order_by('-date')
        submissions = submissions[start:end]
        
        result = []
        
        for submission in submissions:
            submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
            submission.runtime_output = submission_testcases
            result.append(submission)

        problem.testcases = Testcase.objects.filter(problem=problem,deprecated=False)

        submissions_serializer = SubmissionPopulateSubmissionTestcaseAndAccountSerializer(result,many=True)
        problem_serializer = ProblemPopulateTestcaseSerializer(problem)

        return {
            "problem": problem_serializer.data,
            "submissions": submissions_serializer.data,
            "start": start,
            "end": end,
            "total": total,
        }

    def get_submission_by_quries(self, request):
        submissions = Submission.objects.all()
        
        # Query params
        problem_id = str(request.query_params.get("problem_id", ""))
        account_id = str(request.query_params.get("account_id", ""))
        topic_id = str(request.query_params.get("topic_id", ""))
        passed = int(request.query_params.get("passed", -1))
        sort_score = int(request.query_params.get("sort_score", 0))
        sort_date = int(request.query_params.get("sort_date", 0))
        start = int(request.query_params.get("start", -1))
        end = int(request.query_params.get("end", -1))

        if problem_id != "":
            submissions = submissions.filter(problem_id=problem_id)
        if account_id != "":
            submissions = submissions.filter(account_id=account_id)
        if topic_id != "":
            submissions = submissions.filter(problem__topic_id=topic_id)

        if passed == 0:
            submissions = submissions.filter(is_passed=False)
        elif passed == 1:
            submissions = submissions.filter(is_passed=True)

        if sort_score == -1:
            submissions = submissions.order_by('passed_ratio')
        elif sort_score == 1:
            submissions = submissions.order_by('-passed_ratio')

        if sort_date == -1:
            submissions = submissions.order_by('date')
        elif sort_date == 1:
            submissions = submissions.order_by('-date')

        if start != -1 and end != -1:
            submissions = submissions[start:end]

        for submission in submissions:
            submission.runtime_output = SubmissionTestcase.objects.filter(submission=submission)
            
        serialize = SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(submissions,many=True)
        return {"submissions": serialize.data}

    def get_submissions_by_account_problem_in_topic(self, account_id:str,problem_id:str,topic_id:str):
        submissions = Submission.objects.filter(account=account_id,problem=problem_id,topic_id=topic_id)

        if submissions.count() == 0:
            return {"best_submission": None, "submissions": []}

        submissions = submissions.order_by('-date')
        
        result = []
        
        for submission in submissions:
            submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
            submission.runtime_output = submission_testcases
            result.append(submission)
        
        best_submission = BestSubmission.objects.filter(problem=problem_id,topic=topic_id,account=account_id).first()
        if best_submission:
            best_submission.submission.runtime_output = SubmissionTestcase.objects.filter(submission=best_submission.submission)
            best_submission_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(best_submission.submission)
            best_submission_result = best_submission_serializer.data
        else:
            best_submission_result = None

        submissions_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(result,many=True)

        return {"best_submission": best_submission_result, "submissions": submissions_serializer.data}

    def get_submissions_by_account_problem(self, account_id:str,problem_id:str):
        submissions = Submission.objects.filter(account=account_id,problem=problem_id)

        if submissions.count() == 0:
            return {"best_submission": None, "submissions": []}

        submissions = submissions.order_by('-date')
        
        best_submission_id = submissions.order_by('-passed_ratio','-date').first().submission_id

        best_submission = None
        result = []
        
        for submission in submissions:
            submission_testcases = SubmissionTestcase.objects.filter(submission=submission)
            submission.runtime_output = submission_testcases
            result.append(submission)

            if submission.submission_id == best_submission_id:
                best_submission = submission
        
        best_submission_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(best_submission)
        submissions_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(result,many=True)

        return {"best_submission": best_submission_serializer.data, "submissions": submissions_serializer.data}

    def submit_problem_on_topic(self, account_id:str,problem_id:str,topic_id:str,request):
        return self.submit_problem_function(account_id,problem_id,topic_id,request)

    QUEUE = [0,0,0,0,0,0,0,0,0,0]

    def avaliableQueue(self):
        for i in range(len(self.QUEUE)):
            if self.QUEUE[i] == 0:
                return i
        return -1

    def submit_problem_function(self, account_id:str,problem_id:str,topic_id:str,request):
        problem = Problem.objects.get(problem_id=problem_id)
        testcases = Testcase.objects.filter(problem=problem,deprecated=False)
        account = Account.objects.get(account_id=account_id)

        submission_code = request.data['submission_code']
        solution_input = [model_to_dict(i)['input'] for i in testcases]
        solution_output = [model_to_dict(i)['output'] for i in testcases]

        if not regexMatching(problem.submission_regex,submission_code):
            grading_result = '-'*len(solution_input)
        else:
            empty_queue = self.avaliableQueue()
            while empty_queue == -1:
                empty_queue = self.avaliableQueue()
                sleep(5)

            self.QUEUE[empty_queue] = 1
            # grading_result = grader.grading(empty_queue+1,submission_code,solution_input,solution_output)
            grader: ProgramGrader = Grader[request.data['language']]
            grading_result = grader(submission_code,solution_input,empty_queue+1,1.5).grading(solution_output)
            self.QUEUE[empty_queue] = 0

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

        self.problem_service.update_problem_difficulty(problem)

        return testser.data

    def submit_problem(self, account_id:str,problem_id:str,request):
        try:
            return self.submit_problem_function(account_id,problem_id,None,request)
        except Exception as e:
            print(e)
            raise InternalServerError(e)