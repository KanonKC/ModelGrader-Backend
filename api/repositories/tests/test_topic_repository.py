from django.test import TestCase
from api.models import Account, Problem, Topic, Submission, BestSubmission, SubmissionTestcase, Testcase
from api.repositories.topic_repository import TopicRepository
from api.utility import passwordEncryption


class TestGetBestSubmissionsForProblems(TestCase):
    """
    Regression tests for TopicRepository.get_best_submissions_for_problems.

    Unlike ProblemRepository's version (which ranks by passed_ratio/submission_id),
    this method's "best" submission per problem is whatever BestSubmission already
    points to for the given account/topic -- so the tie-break to protect here is
    "one BestSubmission row per problem_id, with runtime_output populated from the
    matching SubmissionTestcase rows in a single extra query" (not N+1).
    """

    def setUp(self):
        self.repo = TopicRepository()
        self.account = Account.objects.create(
            username='tester',
            password=passwordEncryption('password'),
        )
        self.topic = Topic.objects.create(creator=self.account, name='Topic 1')
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

    def _make_submission(self, problem, passed_ratio=1.0):
        return Submission.objects.create(
            problem=problem,
            account=self.account,
            language='python',
            submission_code='print(1)',
            is_passed=True,
            passed_ratio=passed_ratio,
        )

    def test_returns_the_best_submission_linked_for_each_problem(self):
        submission_a = self._make_submission(self.problem_a)
        submission_b = self._make_submission(self.problem_b)
        BestSubmission.objects.create(
            problem=self.problem_a, topic=self.topic, account=self.account, submission=submission_a
        )
        BestSubmission.objects.create(
            problem=self.problem_b, topic=self.topic, account=self.account, submission=submission_b
        )

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id, self.problem_b.problem_id], self.account.account_id, self.topic.topic_id
        )

        self.assertEqual(result[self.problem_a.problem_id].submission_id, submission_a.submission_id)
        self.assertEqual(result[self.problem_b.problem_id].submission_id, submission_b.submission_id)

    def test_populates_runtime_output_from_submission_testcases(self):
        submission_a = self._make_submission(self.problem_a)
        BestSubmission.objects.create(
            problem=self.problem_a, topic=self.topic, account=self.account, submission=submission_a
        )
        testcase = Testcase.objects.create(problem=self.problem_a, input='1', output='1')
        submission_testcase = SubmissionTestcase.objects.create(
            submission=submission_a, testcase=testcase, is_passed=True, runtime_status='AC'
        )

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id], self.account.account_id, self.topic.topic_id
        )

        runtime_output = result[self.problem_a.problem_id].runtime_output
        self.assertEqual(len(runtime_output), 1)
        self.assertEqual(runtime_output[0].submission_testcase_id, submission_testcase.submission_testcase_id)

    def test_problem_without_best_submission_is_absent_from_result(self):
        submission_a = self._make_submission(self.problem_a)
        BestSubmission.objects.create(
            problem=self.problem_a, topic=self.topic, account=self.account, submission=submission_a
        )

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id, self.problem_b.problem_id], self.account.account_id, self.topic.topic_id
        )

        self.assertIn(self.problem_a.problem_id, result)
        self.assertNotIn(self.problem_b.problem_id, result)

    def test_scoped_to_given_topic(self):
        other_topic = Topic.objects.create(creator=self.account, name='Topic 2')
        submission_other_topic = self._make_submission(self.problem_a)
        BestSubmission.objects.create(
            problem=self.problem_a, topic=other_topic, account=self.account, submission=submission_other_topic
        )

        result = self.repo.get_best_submissions_for_problems(
            [self.problem_a.problem_id], self.account.account_id, self.topic.topic_id
        )

        self.assertNotIn(self.problem_a.problem_id, result)
