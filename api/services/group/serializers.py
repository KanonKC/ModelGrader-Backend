from rest_framework import serializers
from ...models import *

# Dependencies
class AccountSecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'username']

# Core Group Serializers
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
