from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

class AccountDetailSerializer(serializers.ModelSerializer):
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

class SubmissionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionOutput
        fields = "__all__"

class TopicProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProblem
        fields = "__all__"

class ProblemSerializer(serializers.ModelSerializer):
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

class TestcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testcase
        fields = "__all__"