from email.policy import default
from random import choices
from secrets import choice
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# Create your models here.
class ProgrammingLanguage(models.TextChoices):
    PYTHON = 'py',_('Python')
    C = 'c',_('C')
    CPP = 'cpp',_('C++')

class Problem(models.Model):
    problem_id = models.AutoField(primary_key=True)
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
    submission_code = models.CharField(max_length=20000)
    result = models.CharField(max_length=100)
    is_passed = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
