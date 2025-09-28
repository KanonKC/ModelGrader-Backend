from rest_framework import serializers
from ...models import *

# Account related serializers (dependencies)
class AccountSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'username']

# Topic related serializers (dependencies)
class TopicSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = ['sharing', 'is_active', 'is_private']

# Group related serializers (dependencies)
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

# Core Problem Serializers
class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"

problem_secure_fields = ['problem_id', 'title', 'description', 'is_active', 'is_private', 'updated_date', 'created_date']

class ProblemSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

class ProblemPopulateAccountSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        fields = "__all__"

class ProblemPopulateAccountSecureSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

# Testcase Serializers
class TestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = "__all__"

class TestcasePartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = ['testcase_id', 'runtime_status']

# Problem with Testcase Serializers
class ProblemPopulatePartialTestcaseSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    testcases = TestcasePartialSerializer(many=True)
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['testcases']

class ProblemPopulateTestcaseSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    testcases = TestcaseSerializer(many=True)
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['testcases']

# Submission Related Serializers
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionTestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = "__all__"

class SubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = ['is_passed', 'runtime_status']

class SubmissionPopulateSubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    class Meta:
        model = Submission
        fields = ['submission_id', 'account', 'problem', 'topic', 'language', 'submission_code', 'is_passed', 'date', 'score', 'max_score', 'passed_ratio', 'runtime_output']

class SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    problem = ProblemSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = ['submission_id', 'account', 'problem', 'topic', 'language', 'submission_code', 'is_passed', 'date', 'score', 'max_score', 'passed_ratio', 'runtime_output']

class SubmissionPoplulateProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionPoplulateProblemSecureSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountSecureSerializer()
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionPopulateSubmissionTestcaseAndAccountSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSerializer(many=True)
    account = AccountSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = "__all__"
        include = ['runtime_output']

# Problem with Submission Serializers
class ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    best_submission = SubmissionPopulateSubmissionTestcaseSecureSerializer()
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['best_submission', 'creator']
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

class ProblemPopulatSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    best_submission = SubmissionPopulateSubmissionTestcaseSecureSerializer()
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['best_submission', 'creator']
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

# Problem Group Permission Serializers
class ProblemGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = ProblemGroupPermission
        fields = "__all__"

class ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    group_permissions = ProblemGroupPermissionsPopulateGroupSerializer(many=True)
    testcases = TestcaseSerializer(many=True)
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['creator', 'group_permissions', 'testcases']

# Collection Problem Serializers
class CollectionProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemPopulateProblemSecureSerializer(serializers.ModelSerializer):
    problem = ProblemSecureSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

# Topic Problem Serializers
class TopicProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProblem
        fields = "__all__"
