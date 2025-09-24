from typing import List
from api.models import Account, Group, Problem, ProblemGroupPermission, Testcase, GroupMember


class ProblemRepository:
    def __init__(self):
        pass

    def create(self,account: Account, pr: Problem, trl: list[Testcase]) -> tuple[Problem, list[Testcase]]:
        problem = Problem(
            language=pr.language,
            creator=account,
            title=pr.title,
            description=pr.description,
            solution=pr.solution,
            time_limit=pr.time_limit,
            allowed_languages=pr.allowed_languages,
        )
        problem.save()

        testcases_result = []
        for unit in trl:
            testcases_result.append(
                Testcase(
                    problem=problem,
                    input=unit.input,
                    output=unit.output,
                    runtime_status=unit.runtime_status
            ))

        Testcase.objects.bulk_create(testcases_result)
        return problem, testcases_result

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

    def get_personal(self, account_id: str, q: str):
        return Problem.objects.filter(creator_id=account_id, title__icontains=q).order_by('-updated_date')

    def get_manageable(self, group_ids: List[str], q: str):
        return Problem.objects.filter(
            problemgrouppermission__permission_manage_problems=True,
            problemgrouppermission__group__in=group_ids,
            title__icontains=q
        ).order_by('-updated_date')

    def get_testcases(self, problem_id: str, deprecated: bool = False):
        return Testcase.objects.filter(problem_id=problem_id, deprecated=deprecated)

    def list_group_permissions(self, problem_id: str):
        return ProblemGroupPermission.objects.filter(problem_id=problem_id)

    def update_group_permission(self, problem_id: str, r: List[ProblemGroupPermission]):
        problem = self.get(problem_id)
        ProblemGroupPermission.objects.filter(problem=problem).delete()
        problem_group_permissions = []
        for group_request in r:
            group = Group.objects.get(group_id=group_request['group_id'])
            problem_group_permissions.append(
                ProblemGroupPermission(
                    problem=problem,
                    group=group,
                    permission_manage_problems=group_request['permission_manage_problems'],
                    permission_view_problems=group_request['permission_view_problems']
            ))

        ProblemGroupPermission.objects.bulk_create(problem_group_permissions)