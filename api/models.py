from email.policy import default
from enum import unique
from random import choices
from secrets import choice
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager

# Create your models here.
class ProgrammingLanguage(models.TextChoices):
    PYTHON = 'py',_('Python')
    C = 'c',_('C')
    CPP = 'cpp',_('C++')

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=256,null=True,default=None)
    token_expire = models.IntegerField(null=True,default=None)

class Problem(models.Model):
    problem_id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    language = models.CharField(max_length=10,choices=ProgrammingLanguage.choices,default=ProgrammingLanguage.PYTHON)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=10000)
    solution = models.CharField(max_length=20000)
    time_limit = models.FloatField(default=1.5,blank=True)

class Testcase(models.Model):
    testcase_id = models.AutoField(primary_key=True)
    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    input = models.CharField(max_length=100000)
    output = models.CharField(max_length=100000)

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,db_column="problem_id")
    account_id = models.ForeignKey(Account,on_delete=models.CASCADE,db_column="account_id")
    submission_code = models.CharField(max_length=20000)
    result = models.CharField(max_length=100)
    is_passed = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)