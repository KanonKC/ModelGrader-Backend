from api.models import Submission, SubmissionTestcase, BestSubmission
from api.utility import group_by
from typing import List


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

    def get_testcases_for_submissions(self, submission_ids: List[str]):
        testcases = SubmissionTestcase.objects.filter(submission_id__in=submission_ids)
        return group_by(testcases, lambda testcase: testcase.submission_id)

    def get_by_problem(self, problem_id: str, start: int = 0, end: int = None):
        submissions = Submission.objects.filter(problem_id=problem_id).select_related('account', 'topic').order_by('-date')
        if end:
            return submissions[start:end]
        return submissions[start:]

    def list(self, problem_id: str = None, account_id: str = None, topic_id: str = None,
             passed: int = None, sort_score: int = 0, sort_date: int = 0,
             start: int = None, end: int = None):
        submissions = Submission.objects.select_related('problem', 'topic').all()
        
        if problem_id:
            submissions = submissions.filter(problem_id=problem_id)
        if account_id:
            submissions = submissions.filter(account_id=account_id)
        if topic_id:
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
        
        if start is not None and end is not None:
            submissions = submissions[start:end]
        
        return submissions
    
    def get_by_account_problem_topic(self, account_id: str, problem_id: str, topic_id: str):
        return Submission.objects.filter(
            account_id=account_id, 
            problem_id=problem_id, 
            topic_id=topic_id
        ).order_by('-date')
    
    def get_by_account_problem(self, account_id: str, problem_id: str):
        return Submission.objects.filter(
            account_id=account_id, 
            problem_id=problem_id
        ).order_by('-date')
    
    def get_best_record(self, problem_id: str, account_id: str, topic_id: str = None):
        if topic_id:
            return BestSubmission.objects.filter(
                problem_id=problem_id, 
                account_id=account_id, 
                topic_id=topic_id
            ).first()
        else:
            return BestSubmission.objects.filter(
                problem_id=problem_id, 
                account_id=account_id
            ).first()
    
    def create(self, submission_data: dict):
        submission = Submission(**submission_data)
        submission.save()
        return submission
    
    def bulk_create_testcases(self, testcases: List[SubmissionTestcase]):
        return SubmissionTestcase.objects.bulk_create(testcases)
    
    def create_or_update_best(self, problem_id: str, account_id: str,
                             submission_id: str, topic_id: str = None):
        if topic_id:
            existing = BestSubmission.objects.filter(
                problem_id=problem_id,
                account_id=account_id,
                topic_id=topic_id
            ).order_by('-best_submission_id')
        else:
            existing = BestSubmission.objects.filter(
                problem_id=problem_id,
                account_id=account_id,
                topic_id__isnull=True
            ).order_by('-best_submission_id')

        best_submission = existing.first()
        # Self-heal duplicate rows left over from a prior race/bug
        BestSubmission.objects.filter(
            best_submission_id__in=[b.best_submission_id for b in existing[1:]]
        ).delete()

        if not best_submission:
            best_submission = BestSubmission(
                problem_id=problem_id,
                account_id=account_id,
                topic_id=topic_id,
                submission_id=submission_id
            )
            best_submission.save()
        else:
            # Update if new submission is better
            current_submission = Submission.objects.get(submission_id=best_submission.submission_id)
            new_submission = Submission.objects.get(submission_id=submission_id)
            
            if new_submission.passed_ratio >= current_submission.passed_ratio:
                best_submission.submission_id = submission_id
                best_submission.save()
        
        return best_submission