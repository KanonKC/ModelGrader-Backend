from email.policy import default
from enum import unique
from random import choices
from secrets import choice
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from .utility import uploadTopic
from uuid import uuid4

def generate_uuid4_hex():
    return uuid4().hex

# Create your models here.
class ProgrammingLanguage(models.TextChoices):
    PYTHON = 'py',_('Python')
    C = 'c',_('C')
    CPP = 'cpp',_('C++')

class Account(models.Model):
    account_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    email = models.EmailField(max_length=50,unique=True,null=True)
    username = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=256,null=True,default=None)
    token_expire = models.IntegerField(null=True,default=None)
    # is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=True)

class Problem(models.Model):
    problem_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    language = models.CharField(max_length=15) # ,choices=ProgrammingLanguage.choices,default=ProgrammingLanguage.PYTHON)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100000)
    solution = models.CharField(max_length=20000)
    time_limit = models.FloatField(default=1.5,blank=True)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    submission_regex = models.CharField(max_length=1000,null=True,blank=True,default=".*")
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
    sharing = models.BooleanField(default=False,blank=True)
    allowed_languages = models.CharField(max_length=1000,blank=True,default="")
    pdf_url = models.FileField(upload_to='import-pdf/',null=True,blank=True,default=None)
    difficulty = models.IntegerField(default=0,blank=True)

class Testcase(models.Model):
    testcase_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    input = models.CharField(max_length=100000)
    output = models.CharField(max_length=100000,null=True)
    runtime_status = models.CharField(max_length=10)
    deprecated = models.BooleanField(default=False,blank=True)

class Collection(models.Model):
    collection_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100000,null=True,blank=True,default=None)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
    sharing = models.BooleanField(default=False,blank=True)


class Topic(models.Model):
    topic_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100000,null=True,blank=True,default=None)
    image_url = models.ImageField(upload_to='topic/',null=True,blank=True,default=None)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
    sharing = models.BooleanField(default=False,blank=True)

class TopicCollection(models.Model):
    id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE,db_column="collection_id")
    order = models.IntegerField(blank=True,default=0)

class CollectionProblem(models.Model):
    id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE,db_column="collection_id")
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    order = models.IntegerField(blank=True,default=0)

# Doesn't use anymore
class TopicProblem(models.Model):
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")

class TopicAccountAccess(models.Model):
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
    account = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")

class Submission(models.Model):
    submission_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id",null=True)
    account = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    language = models.CharField(max_length=15)
    submission_code = models.CharField(max_length=20000)
    is_passed = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    passed_ratio = models.FloatField(default=0)

class SubmissionTestcase(models.Model):
    submission_testcase_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE,db_column="submission_id")
    testcase = models.ForeignKey(Testcase,on_delete=models.CASCADE,db_column="testcase_id")
    output = models.CharField(max_length=100000,blank=True,null=True)
    is_passed = models.BooleanField(default=False,blank=True)
    runtime_status = models.CharField(max_length=10)

class BestSubmission(models.Model):
    best_submission_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id",null=True)
    account = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE,db_column="submission_id")

class Group(models.Model):
    group_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100000,null=True,blank=True,default=None)
    color = models.CharField(max_length=10,null=True,blank=True,default=None)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    permission_manage_topics = models.BooleanField(default=False,blank=True)
    permission_view_topics = models.BooleanField(default=False,blank=True)
    permission_view_topics_log = models.BooleanField(default=False,blank=True)
    permission_manage_collections = models.BooleanField(default=False,blank=True)
    permission_view_collections = models.BooleanField(default=False,blank=True)
    permission_manage_problems = models.BooleanField(default=False,blank=True)
    permission_view_problems = models.BooleanField(default=False,blank=True)

class GroupMember(models.Model):
    group_member_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    group = models.ForeignKey(Group,on_delete=models.CASCADE,db_column="group_id")
    account = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    created_date = models.DateTimeField(default=timezone.now)

class ProblemGroupPermission(models.Model):
    problem_group_permission_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    group = models.ForeignKey(Group,on_delete=models.CASCADE,db_column="group_id")
    permission_manage_problems = models.BooleanField(default=False,blank=True)
    permission_view_problems = models.BooleanField(default=False,blank=True)

class CollectionGroupPermission(models.Model):
    collection_group_permission_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE,db_column="collection_id")
    group = models.ForeignKey(Group,on_delete=models.CASCADE,db_column="group_id")
    permission_manage_collections = models.BooleanField(default=False,blank=True)
    permission_view_collections = models.BooleanField(default=False,blank=True)

class TopicGroupPermission(models.Model):
    topic_group_permission_id = models.CharField(primary_key=True,blank=True,default=generate_uuid4_hex,max_length=32)
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
    group = models.ForeignKey(Group,on_delete=models.CASCADE,db_column="group_id")
    permission_manage_topics = models.BooleanField(default=False,blank=True)
    permission_view_topics = models.BooleanField(default=False,blank=True)
    permission_view_topics_log = models.BooleanField(default=False,blank=True)

# class TopicGroupPermission(models.Model):
#     topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
#     group = models.ForeignKey(Group,on_delete=models.CASCADE,db_column="group_id")
#     permission_access = models.BooleanField(default=False,blank=True)
#     # สามารถเข้าถึง Course นี้ได้ โดยสามารถดูโจทย์ ส่งโจทย์ได้

#     permission_view_problems = models.BooleanField(default=False,blank=True)
#     # เข้าถึงโจทย์เชิงลึกแบบดู Testcases ได้
#     permission_manage_collections = models.BooleanField(default=False,blank=True)
#     # จัดการเพิ่ม/ลบ โจทย์ออกจาก Collection ได้
#     permission_manage_topic = models.BooleanField(default=False,blank=True)
#     # สามารถแก้ไข
#     permission_manage_members = models.BooleanField(default=False,blank=True)
    