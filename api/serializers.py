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
        instance.updated_date = timezone.now()
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
        exclude = ['solution','submission_regex','is_private','is_active','sharing']

class ProblemPopulateAccountSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        fields = "__all__"


class ProblemPopulateAccountSecureSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        exclude = ['solution','submission_regex','is_private','is_active','sharing']



class TopicCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = ['sharing','is_active','is_private']


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

class TestcasePartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = ['testcase_id','runtime_status']
class ProblemPopulatePartialTestcaseSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    testcases = TestcasePartialSerializer(many=True)
    class Meta:
        model = Problem
        fields = "__all__"
        # fields = ['problem_id','title','creator','testcases']
        include = ['testcases']
class ProblemPopulateTestcaseSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    testcases = TestcaseSerializer(many=True)
    class Meta:
        model = Problem
        fields = "__all__"
        include = ['testcases']

# class ProblemPopulateAccountSecureSerializer(serializers.ModelSerializer):
#     creator = AccountSecureSerializer()
#     class Meta:
#         model = Problem
#         fields = ['problem_id','title','description','creator']

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
        fields = ['submission_id','account','problem','topic','language','submission_code','is_passed','date','score','max_score','passed_ratio','runtime_output']

class SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer(serializers.ModelSerializer):
    # Add testcases field
    runtime_output = SubmissionTestcaseSecureSerializer(many=True)
    problem = ProblemSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = ['submission_id','account','problem','topic','language','submission_code','is_passed','date','score','max_score','passed_ratio','runtime_output']

class ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    # Add testcases field
    creator = AccountSecureSerializer()
    best_submission = SubmissionPopulateSubmissionTestcaseSecureSerializer()
    class Meta:
        model = Problem
        # fields = problem_secure_fields + ['best_submission','creator']
        fields = "__all__"
        include = ['best_submission','creator']
        exlude = ['solution','submission_regex','is_private','is_active','sharing']

class ProblemPopulatSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    best_submission = SubmissionPopulateSubmissionTestcaseSecureSerializer()
    class Meta:
        model = Problem
        # fields = problem_secure_fields + ['best_submission']
        fields = "__all__"
        include = ['best_submission','creator']
        exlude = ['solution','submission_regex','is_private','is_active','sharing']
class TopicCollectionPopulateCollectionSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicCollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    collection = CollectionProblemPopulateProblemSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicPopulateTopicCollectionPopulateCollectionSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionSerializer(many=True)
    class Meta:
        model = Topic
        fields = "__all__"
        include = ['collections']


class TopicPopulateTopicCollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    collections = CollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Topic
        fields = ['topic_id','name','description','image_url','is_active','is_private','created_date','updated_date','collections']

class CollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"
class CollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"

class TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    collection = CollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(many=True)
    class Meta:
        model = Topic
        fields = ['topic_id','name','description','image_url','created_date','updated_date','collections']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = "__all__"
class GroupMemberPopulateAccountSecureSerializer(serializers.ModelSerializer):
    account = AccountSecureSerializer()
    class Meta:
        model = GroupMember
        fields = "__all__"

class GroupPopulateGroupMemberPopulateAccountSecureSerializer(serializers.ModelSerializer):
    members = GroupMemberPopulateAccountSecureSerializer(many=True)
    class Meta:
        model = Group
        fields = "__all__"
        include = ['members']

class TopicGroupPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicGroupPermission
        fields = "__all__"

class TopicGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = TopicGroupPermission
        fields = "__all__"

class TopicPopulateTopicGroupPermissionsSerializer(serializers.ModelSerializer):
    group_permissions = TopicGroupPermissionsSerializer(many=True)
    class Meta:
        model = Topic
        fields = "__all__"
        include = ['group_permissions']

class TopicPopulateTopicCollectionPopulateCollectionAndTopicGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionSerializer(many=True)
    group_permissions = TopicGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Topic
        fields = "__all__"
        include = ['collections','group_permissions']

class CollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"

class TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    collection = CollectionPopulateCollectionProblemPopulateProblemSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemAndTopicGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemSerializer(many=True)
    group_permissions = TopicGroupPermissionPopulateGroupSerializer(many=True)

    class Meta:
        model = Topic
        fields = "__all__"
        include = ['collections','group_permissions']

class CollectionGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = CollectionGroupPermission
        fields = "__all__"
class CollectionPopulateCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    group_permissions = CollectionGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['group_permissions']

class CollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    group_permissions = CollectionGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems','group_permissions']



class CollectionPopulateCollectionProblemsPopulateProblemSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems']

class TopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    collection = CollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"
class TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupAndTopicGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(many=True)
    group_permissions = TopicGroupPermissionPopulateGroupSerializer(many=True)

    class Meta:
        model = Topic
        fields = "__all__"
        include = ['collections','group_permissions']

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
        include = ['creator','group_permissions','testcases']


class CollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problem = ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"
class CollectionPopulateCollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupAndCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problems = CollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer(many=True)
    group_permissions = CollectionGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems','group_permissions']

class SubmissionPopulateSubmissionTestcaseAndAccountSerializer(serializers.ModelSerializer):
    runtime_output = SubmissionTestcaseSerializer(many=True)
    account = AccountSecureSerializer()
    topic = TopicSecureSerializer()
    class Meta:
        model = Submission
        fields = "__all__"
        include = ['runtime_output']