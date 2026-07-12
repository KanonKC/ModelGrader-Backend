from django.test import TestCase
from django.utils import timezone
from api.models import Account, Problem, Submission
from api.repositories.problem_repository import ProblemRepository
from api.utility import passwordEncryption


class TestGetBestSubmissionsForProblems(TestCase):
    """
    Regression tests for ProblemRepository.get_best_submissions_for_problems.

    This method replaced a per-problem query loop with a single query ordered by
    ('problem_id', '-passed_ratio', '-submission_id') plus a first-seen-wins dedupe.
    That tie-break is easy to silently break (e.g. reordering the order_by fields),
    so these tests pin down both tie-break dimensions explicitly.
    """

    def setUp(self):
        self.repo = ProblemRepository()
        self.account = Account.objects.create(
            username='tester',
            password=passwordEncryption('password'),
        )
        self.other_account = Account.objects.create(
            username='other',
            password=passwordEncryption('password'),
        )
        self.problem_a = Problem.objects.create(
            creator=self.account,
            language='python',
            title='Problem A',
            description='desc',
            solution='solution',
        )
        self.problem_b = Problem.objects.create(
            creator=self.account,
            language='python',
            title='Problem B',
            description='desc',
            solution='solution',
        )

    def _make_submission(self, problem, account, passed_ratio, is_passed=True):
        return Submission.objects.create(
            problem=problem,
            account=account,
            language='python',
            submission_code='print(1)',
            is_passed=is_passed,
            passed_ratio=passed_ratio,
        )

    def test_picks_highest_passed_ratio_per_problem(self):
        low = self._make_submission(self.problem_a, self.account, passed_ratio=0.5)
        high = self._make_submission(self.problem_a, self.account, passed_ratio=0.9)

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id], self.account.account_id
        )

        self.assertEqual(result[self.problem_a.problem_id].submission_id, high.submission_id)
        self.assertNotEqual(result[self.problem_a.problem_id].submission_id, low.submission_id)

    def test_tie_break_on_submission_id_when_passed_ratio_equal(self):
        first = self._make_submission(self.problem_a, self.account, passed_ratio=1.0)
        second = self._make_submission(self.problem_a, self.account, passed_ratio=1.0)

        expected_winner = max(first.submission_id, second.submission_id)

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id], self.account.account_id
        )

        self.assertEqual(result[self.problem_a.problem_id].submission_id, expected_winner)

    def test_groups_correctly_across_multiple_problems(self):
        best_a = self._make_submission(self.problem_a, self.account, passed_ratio=0.8)
        self._make_submission(self.problem_a, self.account, passed_ratio=0.3)
        best_b = self._make_submission(self.problem_b, self.account, passed_ratio=0.6)
        self._make_submission(self.problem_b, self.account, passed_ratio=0.1)

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id, self.problem_b.problem_id], self.account.account_id
        )

        self.assertEqual(result[self.problem_a.problem_id].submission_id, best_a.submission_id)
        self.assertEqual(result[self.problem_b.problem_id].submission_id, best_b.submission_id)

    def test_only_considers_submissions_for_given_account(self):
        self._make_submission(self.problem_a, self.other_account, passed_ratio=1.0)
        mine = self._make_submission(self.problem_a, self.account, passed_ratio=0.1)

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id], self.account.account_id
        )

        self.assertEqual(result[self.problem_a.problem_id].submission_id, mine.submission_id)
