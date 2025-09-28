from time import sleep
from api.services.problem.problem_service import ProblemService
from api.services.problem.serializers import ProblemPopulateTestcaseSerializer
from api.utility import regexMatching
from api.sandbox.grader import Grader, ProgramGrader
from ...models import *
from django.forms.models import model_to_dict
from .serializers import *
from ...errors.common import *
from api.repositories.submission_repository import SubmissionRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.topic_repository import TopicRepository

class SubmissionService:

    def __init__(self, submission_repo: SubmissionRepository, problem_repo: ProblemRepository, 
        account_repo: AccountRepository, topic_repo: TopicRepository, problem_service: ProblemService):
        self.submission_repo = submission_repo
        self.problem_repo = problem_repo
        self.account_repo = account_repo
        self.topic_repo = topic_repo
        self.problem_service = problem_service

    def get_all_submissions_by_creator_problem(self, problem_id: str, request):
        problem = self.problem_repo.get(problem_id)
        start = int(request.query_params.get("start",0))
        end = int(request.query_params.get("end",-1))
        # query = request.query_params.get("query","")
        if end == -1: end = None

        submissions = self.submission_repo.get_by_problem(problem_id, start, end)
        total = len(submissions)

        if total == 0:
            return {"submissions": []}
        
        result = []
        
        for submission in submissions:
            submission_testcases = self.submission_repo.get_testcases(submission.submission_id)
            submission.runtime_output = submission_testcases
            result.append(submission)

        problem.testcases = self.problem_repo.get_testcases(problem_id, deprecated=False)

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
        # Query params
        problem_id = str(request.query_params.get("problem_id", ""))
        account_id = str(request.query_params.get("account_id", ""))
        topic_id = str(request.query_params.get("topic_id", ""))
        passed = int(request.query_params.get("passed", -1))
        sort_score = int(request.query_params.get("sort_score", 0))
        sort_date = int(request.query_params.get("sort_date", 0))
        start = int(request.query_params.get("start", -1))
        end = int(request.query_params.get("end", -1))

        # Convert empty strings to None for repository method
        problem_id = problem_id if problem_id != "" else None
        account_id = account_id if account_id != "" else None
        topic_id = topic_id if topic_id != "" else None
        passed = passed if passed != -1 else None
        start = start if start != -1 else None
        end = end if end != -1 else None

        submissions = self.submission_repo.list(
            problem_id=problem_id,
            account_id=account_id,
            topic_id=topic_id,
            passed=passed,
            sort_score=sort_score,
            sort_date=sort_date,
            start=start,
            end=end
        )

        for submission in submissions:
            submission.runtime_output = self.submission_repo.get_testcases(submission.submission_id)
            
        serialize = SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(submissions,many=True)
        return {"submissions": serialize.data}

    def get_submissions_by_account_problem_in_topic(self, account_id:str,problem_id:str,topic_id:str):
        submissions = self.submission_repo.get_by_account_problem_topic(account_id, problem_id, topic_id)

        total = len(submissions)
        if total == 0:
            return {"best_submission": None, "submissions": []}
        
        result = []
        
        for submission in submissions:
            submission_testcases = self.submission_repo.get_testcases(submission.submission_id)
            submission.runtime_output = submission_testcases
            result.append(submission)
        
        best_submission = self.submission_repo.get_best_record(problem_id, account_id, topic_id)
        if best_submission:
            best_submission.submission.runtime_output = self.submission_repo.get_testcases(best_submission.submission_id)
            best_submission_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(best_submission.submission)
            best_submission_result = best_submission_serializer.data
        else:
            best_submission_result = None

        submissions_serializer = SubmissionPopulateSubmissionTestcaseSecureSerializer(result,many=True)

        return {"best_submission": best_submission_result, "submissions": submissions_serializer.data}

    def get_submissions_by_account_problem(self, account_id:str,problem_id:str):
        submissions = self.submission_repo.get_by_account_problem(account_id, problem_id)

        total = len(submissions)
        if total == 0:
            return {"best_submission": None, "submissions": []}
        
        best_submission_id = self.submission_repo.get_best(problem_id, account_id).submission_id

        best_submission = None
        result = []
        
        for submission in submissions:
            submission_testcases = self.submission_repo.get_testcases(submission.submission_id)
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
        problem = self.problem_repo.get(problem_id)
        testcases = self.problem_repo.get_testcases(problem_id, deprecated=False)
        account = self.account_repo.get(account_id)

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

        submission_data = {
            'problem_id': problem_id,
            'account_id': account_id,
            'language': request.data['language'],
            'submission_code': request.data['submission_code'],
            'is_passed': grading_result.is_passed,
            'score': total_score,
            'max_score': max_score,
            'passed_ratio': total_score/max_score
        }

        if topic_id:
            submission_data['topic_id'] = topic_id

        submission = self.submission_repo.create(submission_data)

        # Best Submission
        self.submission_repo.create_or_update_best(
            problem_id=problem_id,
            account_id=account_id,
            submission_id=submission.submission_id,
            topic_id=topic_id
        )
        # End Best Submission
                
        submission_testcases = []
        for i in range(len(grading_result.data)):
            submission_testcases.append(SubmissionTestcase(
                submission_id = submission.submission_id,
                testcase_id = testcases[i].testcase_id,
                output = grading_result.data[i].output,
                is_passed = grading_result.data[i].is_passed,
                runtime_status = grading_result.data[i].runtime_status
            ))

        self.submission_repo.bulk_create_testcases(submission_testcases)

        submission.runtime_output = submission_testcases
        testser = SubmissionPopulateSubmissionTestcaseSecureSerializer(submission)

        self.problem_service.update_problem_difficulty(problem)

        return testser.data

    def submit_problem(self, account_id:str,problem_id:str,request):
        try:
            return self.submit_problem_function(account_id,problem_id,None,request)
        except Exception as e:
            raise InternalServerError(e)