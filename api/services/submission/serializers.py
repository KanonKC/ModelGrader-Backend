from rest_framework import serializers
from api.models import *
from api.services.problem.serializers import ProblemSecureSerializer, TopicSecureSerializer
from api.services.account.serializers import AccountSecureSerializer

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = "__all__"

class SubmissionTestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = "__all__"

class SubmissionPopulateSubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    class Meta:
        model = Submission
        fields = ['submission_id','account','problem','topic','language','submission_code','is_passed','date','score','max_score','passed_ratio','runtime_output']

class SubmissionPopulateSubmissionTestcaseAndAccountSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSerializer(many=True)
    account = AccountSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = "__all__"
        include = ['runtime_output']

class SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    problem = ProblemSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = ['submission_id','account','problem','topic','language','submission_code','is_passed','date','score','max_score','passed_ratio','runtime_output']