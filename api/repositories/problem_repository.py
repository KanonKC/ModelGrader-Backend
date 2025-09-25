from typing import List
from django.utils import timezone
from api.models import Problem, Testcase, Submission, SubmissionTestcase, BestSubmission


class ProblemRepository:
    def __init__(self):
        pass

    def create(self, data: dict) -> Problem:
        problem = Problem(**data)
        problem.save()
        return problem

    def list(self, filters: dict = {}, order_by: list[str] = []):
        problems = Problem.objects.all()
        if 'is_private' in filters and filters['is_private'] is not None:
            problems = problems.filter(is_private=filters['is_private'])
        if 'is_active' in filters and filters['is_active'] is not None:
            problems = problems.filter(is_active=filters['is_active'])
        if 'creator_id' in filters and filters['creator_id'] is not None:
            problems = problems.filter(creator_id=filters['creator_id'])
        if 'id_list' in filters and filters['id_list'] is not None:
            problems = problems.filter(problem_id__in=filters['id_list'])
        problems = problems.order_by(*order_by)
        return problems

    def get(self, id: str):
        return Problem.objects.get(problem_id=id)

    def delete(self, id: str):
        problem = Problem.objects.get(problem_id=id)
        problem.delete()

    def delete_many(self, id_list: List[str]):
        Problem.objects.filter(problem_id__in=id_list).delete()

    def get_personal(self, account_id: str, q: str, start: int = 0, end: int = None):
        problems = Problem.objects.filter(creator_id=account_id, title__icontains=q).order_by('-updated_date')
        if end:
            return problems[start:end]
        return problems
    
    def get_by_creator(self, account_id: str):
        return Problem.objects.filter(creator_id=account_id).order_by('-updated_date')

    def get_testcases(self, problem_id: str, deprecated: bool = False):
        return Testcase.objects.filter(problem_id=problem_id, deprecated=deprecated)
    
    def create_testcase(self, data: dict) -> Testcase:
        testcase = Testcase(**data)
        testcase.save()
        return testcase
    
    def bulk_create_testcases(self, testcases: List[Testcase]):
        Testcase.objects.bulk_create(testcases)
    
    def deprecate_testcases(self, problem_id: str):
        testcases = Testcase.objects.filter(problem_id=problem_id, deprecated=False)
        for testcase in testcases:
            testcase.deprecated = True
            testcase.save()
    
    def update(self, problem_id: str, data: dict):
        problem = self.get(problem_id)
        for key, value in data.items():
            if hasattr(problem, key):
                setattr(problem, key, value)
        problem.updated_date = timezone.now()
        problem.save()
        return problem
    
    def get_with_best_submission(self, account_id: str):
        return Problem.objects.all().order_by('-updated_date')
    
    def get_best_submission(self, problem_id: str, account_id: str):
        return Submission.objects.filter(problem_id=problem_id, account_id=account_id).order_by('-passed_ratio', '-submission_id').first()
    
    def get_best_submission_in_topic(self, problem_id: str, account_id: str, topic_id: str):
        return BestSubmission.objects.filter(problem_id=problem_id, account_id=account_id, topic_id=topic_id).first()
    
    def get_submission_testcases(self, submission_id: str):
        return SubmissionTestcase.objects.filter(submission_id=submission_id)
    
    def get_submissions_by_problem(self, problem_id: str):
        return Submission.objects.filter(problem_id=problem_id)
    
    def get_manageable_by_account(self, group_ids: List[str], query: str = '', start: int = 0, end: int = None):
        """Get problems manageable by account through group permissions"""
        problems = Problem.objects.filter(
            problemgrouppermission__permission_manage_problems=True,
            problemgrouppermission__group__in=group_ids,
            title__icontains=query
        ).order_by('-updated_date')
        if end:
            return problems[start:end]
        return problems