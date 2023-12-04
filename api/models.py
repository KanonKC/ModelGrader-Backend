from email.policy import default
from enum import unique
from random import choices
from secrets import choice
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from .utility import uploadTopic

# Create your models here.
class ProgrammingLanguage(models.TextChoices):
    PYTHON = 'py',_('Python')
    C = 'c',_('C')
    CPP = 'cpp',_('C++')

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50,unique=True,null=True)
    username = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=256,null=True,default=None)
    token_expire = models.IntegerField(null=True,default=None)
    # is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=True)

class Problem(models.Model):
    problem_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    language = models.CharField(max_length=15) # ,choices=ProgrammingLanguage.choices,default=ProgrammingLanguage.PYTHON)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=10000)
    solution = models.CharField(max_length=20000)
    time_limit = models.FloatField(default=1.5,blank=True)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    submission_regex = models.CharField(max_length=1000,null=True,blank=True,default=".*")
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
    

class Testcase(models.Model):
    testcase_id = models.AutoField(primary_key=True)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    input = models.CharField(max_length=100000)
    output = models.CharField(max_length=100000)
    runtime_status = models.CharField(max_length=10)

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    account = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    language = models.CharField(max_length=15)
    submission_code = models.CharField(max_length=20000)
    is_passed = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    passed_ratio = models.FloatField(default=0)

class Collection(models.Model):
    collection_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000,null=True,blank=True,default=None)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)

class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="creator_id")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000,null=True,blank=True,default=None)
    image_url = models.ImageField(upload_to='topic/',null=True,blank=True,default=None)
    is_active = models.BooleanField(default=True,blank=True)
    is_private = models.BooleanField(default=False,blank=True)

class TopicCollection(models.Model):
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,db_column="topic_id")
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE,db_column="collection_id")
    order = models.IntegerField(blank=True,default=0)

class CollectionProblem(models.Model):
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

class SubmissionTestcase(models.Model):
    submission_testcase_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE,db_column="submission_id")
    testcase = models.ForeignKey(Testcase,on_delete=models.CASCADE,db_column="testcase_id")
    output = models.CharField(max_length=100000,blank=True,null=True)
    is_passed = models.BooleanField(default=False,blank=True)
    runtime_status = models.CharField(max_length=10)