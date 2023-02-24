from rest_framework import serializers
from .models import *

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

class TopicProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProblem
        fields = "__all__"

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = "__all__"