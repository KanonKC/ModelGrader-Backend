from api.models import Submission, SubmissionTestcase


class SubmissionRepository:
    def __init__(self):
        pass

    def get_best(self, problem_id: str, account_id: str, topic_id: str = None):
        submissions = Submission.objects.filter(
            problem_id=problem_id,
            account_id=account_id
        )

        if topic_id is not None:
            submissions = submissions.filter(topic_id=topic_id)
        
        submissions = submissions.order_by('-passed_ratio', '-submission_id')
        
        return submissions.first()

    def get_testcases(self, submission_id: str):
        return SubmissionTestcase.objects.filter(submission_id=submission_id)