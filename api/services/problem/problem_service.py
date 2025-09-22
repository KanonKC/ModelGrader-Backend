from django.utils import timezone
from api.repositories.group_repository import GroupRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.submission_repository import SubmissionRepository
from api.repositories.topic_repository import TopicRepository
from api.sandbox.grader import PythonGrader, Grader, ProgramGrader, RuntimeResultList
from ...models import *
from .serializers import *
from ...difficulty_predictor.preprocess import *
from ...difficulty_predictor.predictor import *
from ...errors.common import *
from ...repositories.account_repository import AccountRepository

try:
    import pandas as pd
    pd.options.mode.chained_assignment = None
    pandas_success = True
except:
    pandas_success = False

class ProblemService:

    def __init__(self):
        pass

    def create_problem(self, account_id: str, request):
        account = Account.objects.get(account_id=account_id)
        running_result = PythonGrader(request.data['solution'], request.data['testcases'], 1, 1.5).generate_output()

        problem = Problem(
            language=request.data['language'],
            creator=account,
            title=request.data['title'],
            description=request.data['description'],
            solution=request.data['solution'],
            time_limit=request.data['time_limit'],
            allowed_languages=request.data['allowed_languages'],
        )
        problem.save()

        testcases_result = []
        for unit in running_result.data:
            testcases_result.append(
                Testcase(
                    problem=problem,
                    input=unit.input,
                    output=unit.output,
                    runtime_status=unit.runtime_status
            ))

        Testcase.objects.bulk_create(testcases_result)

        problem_serialize = ProblemSerializer(problem)
        testcases_serialize = TestcaseSerializer(testcases_result, many=True)

        return {**problem_serialize.data, 'testcases': testcases_serialize.data}

    def delete_problem(self, problem_id: str):
        problem = Problem.objects.get(problem_id=problem_id)
        testcases = Testcase.objects.filter(problem=problem)
        problem.delete()
        testcases.delete()
        return None

    def validate_program(self, request):
        grader: ProgramGrader = Grader[request.data['language']]
        result: RuntimeResultList = grader(request.data['source_code'], request.data['testcases'], 1, request.data['time_limited']).generate_output()

        print(result.getResult())
        print(result.runnable)

        return {
            'runnable': result.runnable,
            'has_error': result.has_error,
            'has_timeout': result.has_timeout,
            'runtime_results': result.getResult(),
        }

    def import_elabsheet_problem(self, request, problem_id: str):
        problem = Problem.objects.get(problem_id=problem_id)
        print("importing elabsheet problem")
        print(request.data)
        # Get file
        file = request.data.get('file')
        problem.pdf_url = file
        print(file)
        print(problem.pdf_url)
        return None

    def get_all_problems_by_account(self, account_id: str, request):
        account = Account.objects.get(account_id=account_id)
        start = int(request.query_params.get("start", 0))
        end = int(request.query_params.get("end", -1))
        query = request.query_params.get("query", "")
        if end == -1: 
            end = None

        personalProblems = Problem.objects.filter(creator=account, title__icontains=query).order_by('-updated_date')
        maxPersonal = len(personalProblems)
        if start < maxPersonal and start < maxPersonal:
            personalProblems = personalProblems[start:end]
        for problem in personalProblems:
            problem.testcases = Testcase.objects.filter(problem=problem, deprecated=False)

        manageableProblems = Problem.objects.filter(
            problemgrouppermission__permission_manage_problems=True,
            problemgrouppermission__group__in=GroupMember.objects.filter(account=account).values_list("group", flat=True),
            title__icontains=query
        ).order_by('-updated_date')
        maxManageable = len(manageableProblems)
        if start < maxManageable and start < maxManageable:
            manageableProblems = manageableProblems[start:end]
        for problem in manageableProblems:
            problem.testcases = Testcase.objects.filter(problem=problem, deprecated=False)

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
        account = Account.objects.get(account_id=account_id)
        problems = Problem.objects.all().order_by('-updated_date')

        for problem in problems:
            best_submission = Submission.objects.filter(problem=problem, account=account).order_by('-passed_ratio', '-submission_id').first()
            if not (best_submission is None):
                testcases = SubmissionTestcase.objects.filter(submission=best_submission)
                best_submission.runtime_output = testcases
                problem.best_submission = best_submission
            else:
                problem.best_submission = None
        
        problem_ser = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problems, many=True)
        return {"problems": problem_ser.data}

    def get_all_problems(self, request):
        problem = Problem.objects.all()

        get_private = int(request.query_params.get("private", 0))
        get_deactive = int(request.query_params.get("deactive", 0))
        account_id = str(request.query_params.get("account_id", ""))
        
        if not get_private:
            problem = problem.filter(is_private=False)
        if not get_deactive:
            problem = problem.filter(is_active=True)
        if account_id != "":
            problem = problem.filter(creator_id=account_id)

        problem = problem.order_by('-problem_id')

        serialize = ProblemPopulateAccountSerializer(problem, many=True)

        return {'problems': serialize.data}

    def get_problem(self, problem_id: str):
        problem = Problem.objects.get(problem_id=problem_id)
        problem.testcases = Testcase.objects.filter(problem=problem, deprecated=False)
        problem.group_permissions = ProblemGroupPermission.objects.filter(problem=problem)

        serialize = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(problem)

        return serialize.data

    def get_problem_in_topic_with_best_submission(self, account_id: str, topic_id: str, problem_id: int):
        account = Account.objects.get(account_id=account_id)
        problem = Problem.objects.get(problem_id=problem_id)
        topic = Topic.objects.get(topic_id=topic_id)

        best_submission = BestSubmission.objects.filter(problem=problem, topic=topic, account=account).first()
        if not (best_submission is None):
            testcases = SubmissionTestcase.objects.filter(submission=best_submission.submission)
            print(testcases)
            best_submission.runtime_output = testcases
            problem.best_submission = best_submission
        else:
            problem.best_submission = None
        
        serialize = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(problem)
        return serialize.data

    def get_problem_public(self, problem_id: str):
        problem = Problem.objects.get(problem_id=problem_id)
        serialize = ProblemPopulateAccountSecureSerializer(problem)
        return serialize.data

    def remove_bulk_problems(self, request):
        target = request.data.get("problem", [])
        problems = Problem.objects.filter(problem_id__in=target)
        problems.delete()
        return None

    def update_group_permission_to_problem(self, problem_id: str, request):
        problem = Problem.objects.get(problem_id=problem_id)
        ProblemGroupPermission.objects.filter(problem=problem).delete()

        problem_group_permissions = []
        for group_request in request.data['groups']:
            group = Group.objects.get(group_id=group_request['group_id'])
            problem_group_permissions.append(
                ProblemGroupPermission(
                    problem=problem,
                    group=group,
                    **group_request
            ))

        ProblemGroupPermission.objects.bulk_create(problem_group_permissions)

        problem.group_permissions = problem_group_permissions
        problem.testcases = Testcase.objects.filter(problem=problem)
        
        serialize = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(problem)
        return serialize.data

    def update_problem(self, problem_id: str, request):
        problem = Problem.objects.get(problem_id=problem_id)
        testcases = Testcase.objects.filter(problem=problem, deprecated=False)

        problem.title = request.data.get("title", problem.title)
        problem.language = request.data.get("language", problem.language)
        problem.description = request.data.get("description", problem.description)
        problem.solution = request.data.get("solution", problem.solution)
        problem.time_limit = request.data.get("time_limit", problem.time_limit)  
        problem.is_private = request.data.get("is_private", problem.is_private)
        problem.allowed_languages = request.data.get("allowed_languages", problem.allowed_languages)

        problem.updated_date = timezone.now()

        if 'testcases' in request.data:
            running_result = Grader[request.data['language']](problem.solution, request.data['testcases'], 1, 1.5).generate_output()

            # if not running_result.runnable:
            #     raise BadRequestError('Error during editing. Your code may has an error/timeout!')
            for testcase in testcases:
                testcase.deprecated = True
                testcase.save()
            testcase_result = []
            for unit in running_result.data:
                testcase2 = Testcase(
                    problem=problem,
                    input=unit.input,
                    output=unit.output,
                    runtime_status=unit.runtime_status
                )
                testcase2.save()
                testcase_result.append(testcase2)
            problem.save()
            problem_serialize = ProblemSerializer(problem)
            testcases_serialize = TestcaseSerializer(testcase_result, many=True)

            return {**problem_serialize.data, 'testcases': testcases_serialize.data}
        
        if 'solution' in request.data:
            testcases = Testcase.objects.filter(problem=problem, deprecated=False)
            program_input = [i.input for i in testcases]
            running_result = Grader[request.data['language']](problem.solution, program_input, 1, 1.5).generate_output()

            if not running_result.runnable:
                raise BadRequestError('Error during editing. Your code may has an error/timeout!')

        problem.save()
        problem_serialize = ProblemSerializer(problem)
        return problem_serialize.data

    def update_problem_difficulty(self, problem_id: str):
        problem = Problem.objects.get(problem_id=problem_id)
        if not pandas_success:
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

        [total_attempt, time_used] = modelgrader_preprocessor(df)
        difficulty = predict(total_attempt, time_used)
        
        problem.difficulty = difficulty
        problem.save()
