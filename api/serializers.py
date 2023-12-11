from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

class AccountSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id','username']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"
    
    def create(self,validate_data):
        return Topic.objects.create(**validate_data)

    def update(self,instance,validate_data):
        instance.name = validate_data.get('name',instance.name)
        instance.description = validate_data.get('description',instance.description)
        instance.image_url = validate_data.get('image_url',instance.image_url)
        instance.is_active = validate_data.get('is_active',instance.is_active)
        instance.is_private = validate_data.get('is_private',instance.is_private)
        instance.save()
        return instance
    
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"

class TopicProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProblem
        fields = "__all__"

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"

problem_secure_fields = ['problem_id','title','description','is_active','is_private','updated_date','created_date']
class ProblemSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['problem_id','title','description','is_active','is_private','updated_date','created_date']

class ProblemPopulateAccountSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        fields = "__all__"

class TopicCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCollection
        fields = "__all__"

class CollectionProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemPopulateProblemSecureSerializer(serializers.ModelSerializer):
    problem = ProblemSecureSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"
    
    def create(self,validate_data):
        return Collection.objects.create(**validate_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.description = validated_data.get('description',instance.description)
        instance.is_active = validated_data.get('is_active',instance.is_active)
        instance.is_private = validated_data.get('is_private',instance.is_private)

        instance.save()
        return instance

class TopicAccountAccessSerialize(serializers.ModelSerializer):
    class Meta:
        model = TopicAccountAccess
        fields = "__all__"

class SubmissionPoplulateProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionTestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = "__all__"

class TestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = "__all__"

class ProblemPopulateTestcaseSerializer(serializers.ModelSerializer):
    testcases = TestcaseSerializer(many=True)
    class Meta:
        model = Problem
        fields = [
            'problem_id',
            'language',
            'title',
            'description',
            'solution',
            'time_limit',
            'is_active',
            'is_private',
            'submission_regex',
            'created_date',
            'updated_date',
            'creator',
            'testcases'
        ]

class ProblemPopulateAccountSecureSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        fields = ['problem_id','title','description','creator']

class SubmissionPoplulateProblemSecureSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountSecureSerializer()
    class Meta:
        model = Submission
        fields = "__all__"

class SubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestcase
        fields = ['is_passed','runtime_status']

class SubmissionPopulateSubmissionTestcaseSecureSerializer(serializers.ModelSerializer):
    # Add testcases field
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    class Meta:
        model = Submission
        fields = ['submission_id','problem','language','submission_code','is_passed','date','score','max_score','passed_ratio','runtime_output']

class ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    # Add testcases field
    creator = AccountSecureSerializer()
    best_submission = SubmissionPopulateSubmissionTestcaseSecureSerializer()
    class Meta:
        model = Problem
        fields = problem_secure_fields + ['best_submission','creator']