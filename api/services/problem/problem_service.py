from django.utils import timezone
from api.repositories.group_repository import GroupRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.submission_repository import SubmissionRepository
from api.repositories.topic_repository import TopicRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.account_repository import AccountRepository
from api.sandbox.grader import ProgramGrader, RuntimeResultList
from ...models import *
from .serializers import *
from ...difficulty_predictor.preprocess import *
from ...difficulty_predictor.predictor import *
from ...errors.common import *

try:
    import pandas as pd
    pd.options.mode.chained_assignment = None
    pandas_success = True
except:
    pandas_success = False

class ProblemService:

    def __init__(self, problem_repo: ProblemRepository, account_repo: AccountRepository, permission_repo: PermissionRepository, group_repo: GroupRepository, topic_repo: TopicRepository, grader: dict[ProgramGrader]):
        self.problem_repo = problem_repo
        self.account_repo = account_repo
        self.permission_repo = permission_repo
        self.group_repo = group_repo
        self.topic_repo = topic_repo
        self.grader = grader

    def create_problem(self, account_id: str, request):
        account = self.account_repo.get(account_id)
        python_grader: ProgramGrader = self.grader['python']
        running_result = python_grader(request.data['solution'], request.data['testcases'], 1, 1.5).generate_output()

        problem_data = {
            'language': request.data['language'],
            'creator': account,
            'title': request.data['title'],
            'description': request.data['description'],
            'solution': request.data['solution'],
            'time_limit': request.data['time_limit'],
            'allowed_languages': request.data['allowed_languages'],
            'view_mode': request.data.get('view_mode', 'plate'),
            'pdf_url': request.data.get('pdf_url', None),
        }
        problem = self.problem_repo.create(problem_data)

        testcases_result = []
        for unit in running_result.data:
            testcases_result.append(
                Testcase(
                    problem=problem,
                    input=unit.input,
                    output=unit.output,
                    runtime_status=unit.runtime_status
            ))

        self.problem_repo.bulk_create_testcases(testcases_result)

        problem_serialize = ProblemSerializer(problem)
        testcases_serialize = TestcaseSerializer(testcases_result, many=True)

        return {**problem_serialize.data, 'testcases': testcases_serialize.data}

    def delete_problem(self, problem_id: str):
        self.problem_repo.delete(problem_id)
        return None

    def validate_program(self, request):
        grader: ProgramGrader = self.grader[request.data['language']]
        result: RuntimeResultList = grader(request.data['source_code'], request.data['testcases'], 1, request.data['time_limited']).generate_output()

        return {
            'runnable': result.runnable,
            'has_error': result.has_error,
            'has_timeout': result.has_timeout,
            'runtime_results': result.getResult(),
        }

    # def import_elabsheet_problem(self, request, problem_id: str):
    #     # Get file
    #     file = request.data.get('file')
    #     self.problem_repo.update(problem_id, {'pdf_url': file})
    #     return None

    def get_all_problems_by_account(self, account_id: str, request):
        start = int(request.query_params.get("start", 0))
        end = int(request.query_params.get("end", -1))
        query = request.query_params.get("query", "")
        if end == -1: 
            end = None

        personalProblems = list(self.problem_repo.get_personal(account_id, query, start, end))
        maxPersonal = len(personalProblems)
        personalTestcases = self.problem_repo.get_testcases_for_problems(
            [problem.problem_id for problem in personalProblems], deprecated=False
        )
        for problem in personalProblems:
            problem.testcases = personalTestcases.get(problem.problem_id, [])

        group_ids = self.group_repo.get_by_creator(account_id)
        manageableProblems = list(self.problem_repo.get_manageable_by_account(group_ids, query, start, end))
        maxManageable = len(manageableProblems)
        manageableTestcases = self.problem_repo.get_testcases_for_problems(
            [problem.problem_id for problem in manageableProblems], deprecated=False
        )
        for problem in manageableProblems:
            problem.testcases = manageableTestcases.get(problem.problem_id, [])

        personalSerialize = ProblemPopulatePartialTestcaseSerializer(personalProblems, many=True)
        manageableSerialize = ProblemPopulatePartialTestcaseSerializer(manageableProblems, many=True)

        return {
            "start": start,
            "end": end,
            "total_personal_problems": maxPersonal,
            "total_manageable_problems": maxManageable,
            "problems": personalSerialize.data,
            "manageable_problems": manageableSerialize.data
        }

    def get_all_problem_with_best_submission(self, account_id: str):
        problems = list(self.problem_repo.get_with_best_submission(account_id))

        best_by_problem = self.problem_repo.get_best_submissions_for_problems(
            [problem.problem_id for problem in problems], account_id
        )
        testcases_by_submission = self.problem_repo.get_submission_testcases_for_submissions(
            [submission.submission_id for submission in best_by_problem.values()]
        )

        for problem in problems:
            best_submission = best_by_problem.get(problem.problem_id)
            if best_submission:
                best_submission.runtime_output = testcases_by_submission.get(best_submission.submission_id, [])
                problem.best_submission = best_submission
            else:
                problem.best_submission = None

        problem_ser = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problems, many=True)
        return {"problems": problem_ser.data}

    def get_all_problems(self, request):
        get_private = int(request.query_params.get("private", 0))
        get_deactive = int(request.query_params.get("deactive", 0))
        account_id = str(request.query_params.get("account_id", ""))
        
        filters = {}
        if not get_private:
            filters['is_private'] = False
        if not get_deactive:
            filters['is_active'] = True
        if account_id != "":
            filters['creator_id'] = account_id

        problems = self.problem_repo.list(filters=filters, order_by=['-problem_id'])
        serialize = ProblemPopulateAccountSerializer(problems, many=True)

        return {'problems': serialize.data}

    def get_problem(self, problem_id: str):
        problem = self.problem_repo.get(problem_id)
        problem.testcases = self.problem_repo.get_testcases(problem_id, deprecated=False)
        problem.group_permissions = self.permission_repo.get_problem_permissions(problem_id)

        serialize = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(problem)

        return serialize.data

    def get_problem_in_topic_with_best_submission(self, account_id: str, topic_id: str, problem_id: int):
        problem = self.problem_repo.get(problem_id)

        best_submission = self.problem_repo.get_best_submission_in_topic(problem_id, account_id, topic_id)
        if best_submission:
            testcases = self.problem_repo.get_submission_testcases(best_submission.submission.submission_id)
            best_submission.runtime_output = testcases
            problem.best_submission = best_submission
        else:
            problem.best_submission = None
        
        serialize = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problem)
        return serialize.data

    def get_problem_public(self, problem_id: str):
        problem = self.problem_repo.get(problem_id)
        serialize = ProblemPopulateAccountSecureSerializer(problem)
        return serialize.data

    def remove_bulk_problems(self, request):
        target = request.data.get("problem", [])
        self.problem_repo.delete_many(target)
        return None

    def update_group_permission_to_problem(self, problem_id: str, request):
        problem = self.problem_repo.get(problem_id)
        self.permission_repo.delete_problem_permissions(problem_id)

        problem_group_permissions = []
        for group_request in request.data['groups']:
            group = self.group_repo.get(group_request['group_id'])
            problem_group_permissions.append(
                ProblemGroupPermission(
                    problem=problem,
                    group=group,
                    **group_request
            ))

        self.permission_repo.bulk_create_problem_permissions(problem_group_permissions)

        problem.group_permissions = problem_group_permissions
        problem.testcases = self.problem_repo.get_testcases(problem_id)
        
        serialize = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(problem)
        return serialize.data

    def update_problem(self, problem_id: str, request):
        update_data = {
            'title': request.data.get('title'),
            'language': request.data.get('language'),
            'description': request.data.get('description'),
            'solution': request.data.get('solution'),
            'time_limit': request.data.get('time_limit'),
            'is_private': request.data.get('is_private'),
            'allowed_languages': request.data.get('allowed_languages'),
            'view_mode': request.data.get('view_mode'),
            'pdf_url': request.data.get('pdf_url'),
        }
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        problem = self.problem_repo.update(problem_id, update_data)

        if 'testcases' in request.data:
            running_result = self.grader[request.data['language']](problem.solution, request.data['testcases'], 1, 1.5).generate_output()

            # if not running_result.runnable:
            #     raise BadRequestError('Error during editing. Your code may has an error/timeout!')
            self.problem_repo.deprecate_testcases(problem_id)
            
            testcase_result = []
            for unit in running_result.data:
                testcase_data = {
                    'problem': problem,
                    'input': unit.input,
                    'output': unit.output,
                    'runtime_status': unit.runtime_status
                }
                testcase = self.problem_repo.create_testcase(testcase_data)
                testcase_result.append(testcase)
                
            problem_serialize = ProblemSerializer(problem)
            testcases_serialize = TestcaseSerializer(testcase_result, many=True)

            return {**problem_serialize.data, 'testcases': testcases_serialize.data}
        
        if 'solution' in request.data:
            testcases = self.problem_repo.get_testcases(problem_id, deprecated=False)
            program_input = [i.input for i in testcases]
            running_result = self.grader[request.data['language']](problem.solution, program_input, 1, 1.5).generate_output()

            if not running_result.runnable:
                raise BadRequestError('Error during editing. Your code may has an error/timeout!')

        problem_serialize = ProblemSerializer(problem)
        return problem_serialize.data

    def update_problem_difficulty(self, problem_id: str):
        if not pandas_success:
            return

        submissions = self.problem_repo.get_submissions_for_difficulty(problem_id)

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

        [total_attempt, time_used] = modelgrader_preprocessor(df)
        difficulty = predict(total_attempt, time_used)
        
        self.problem_repo.update(problem_id, {'difficulty': difficulty})
