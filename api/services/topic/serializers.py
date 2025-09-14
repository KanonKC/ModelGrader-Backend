from rest_framework import serializers
from django.utils import timezone
from ...models import *

# Dependencies
class AccountSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"

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

# Core Topic Serializers
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"
    
    def create(self, validate_data):
        return Topic.objects.create(**validate_data)

    def update(self, instance, validate_data):
        instance.name = validate_data.get('name', instance.name)
        instance.description = validate_data.get('description', instance.description)
        instance.image_url = validate_data.get('image_url', instance.image_url)
        instance.is_active = validate_data.get('is_active', instance.is_active)
        instance.is_private = validate_data.get('is_private', instance.is_private)
        instance.updated_date = timezone.now()
        instance.save()
        return instance
    
class TopicSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        exclude = ['sharing', 'is_active', 'is_private']

# Topic Collection Serializers
class TopicCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicCollectionPopulateCollectionSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()
    class Meta:
        model = TopicCollection
        fields = "__all__"

class TopicPopulateTopicCollectionPopulateCollectionSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionSerializer(many=True)
    class Meta:
        model = Topic
        fields = "__all__"
        include = ['collections']

# Collection Problem Serializers (needed for topic functionality)
class CollectionProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionProblem
        fields = "__all__"

class CollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()
    class Meta:
        model = CollectionProblem
        fields = "__all__"

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

class TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemSerializer(serializers.ModelSerializer):
    collections = TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Topic
        fields = ['topic_id', 'name', 'description', 'image_url', 'is_active', 'is_private', 'created_date', 'updated_date', 'collections']

# Topic Group Permission Serializers
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
        include = ['collections', 'group_permissions']

# Collection Group Permission Serializers (needed for topic functionality)
class CollectionGroupPermissionPopulateGroupSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = CollectionGroupPermission
        fields = "__all__"

class CollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupSerializer(serializers.ModelSerializer):
    problems = CollectionProblemPopulateProblemSerializer(many=True)
    group_permissions = CollectionGroupPermissionPopulateGroupSerializer(many=True)
    class Meta:
        model = Collection
        fields = "__all__"
        include = ['problems', 'group_permissions']

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
        include = ['collections', 'group_permissions']

# Complex Submission Integration Serializers (simplified to avoid circular imports)
class TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(serializers.ModelSerializer):
    # Note: This would need submission serializers, using basic problem serializer to avoid circular imports
    collections = TopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemSerializer(many=True)
    class Meta:
        model = Topic
        fields = ['topic_id', 'name', 'description', 'image_url', 'created_date', 'updated_date', 'collections']

# Topic Problem Serializers (legacy)
class TopicProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProblem
        fields = "__all__"

# Topic Account Access Serializers
class TopicAccountAccessSerialize(serializers.ModelSerializer):
    class Meta:
        model = TopicAccountAccess
        fields = "__all__"
