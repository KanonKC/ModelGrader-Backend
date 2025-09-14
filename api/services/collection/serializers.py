from rest_framework import serializers
from ...models import *

# Dependencies - Account, Group, Topic, Problem serializers
class AccountSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class TopicSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = ['sharing', 'is_active', 'is_private']

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"

class ProblemSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

class ProblemPopulateAccountSecureSerializer(serializers.ModelSerializer):
    creator = AccountSecureSerializer()
    class Meta:
        model = Problem
        exclude = ['solution', 'submission_regex', 'is_private', 'is_active', 'sharing']

class TestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = "__all__"

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

# Core Collection Serializers
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"
    
    def create(self, validate_data):
        return Collection.objects.create(**validate_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_private = validated_data.get('is_private', instance.is_private)
        instance.save()
        return instance

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
    # Note: This serializer requires problem serializers with submission data
    # For now, using basic problem serializer to avoid circular imports
    problem = ProblemPopulateAccountSecureSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

# Collection Group Permission Serializers
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

# Complex Collection Serializers with Problems
class CollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"

class CollectionPopulateCollectionProblemsPopulateProblemSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems']

class CollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"

class CollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    group_permissions = CollectionGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems', 'group_permissions']

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
        include = ['problems', 'group_permissions']

# Topic Collection Serializers (for integration)
class TopicCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicCollectionPopulateCollectionSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"
