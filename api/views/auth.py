import re
from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from uuid import uuid4
from time import time
from decouple import config

from ..controllers.auth.authorization import *
from ..controllers.auth.login import *
from ..controllers.auth.logout import *

TOKEN_LIFETIME = int(config('TOKEN_LIFETIME_SECOND')) # (Second)

@api_view([POST])
def login_view(request):
    return login(request)

@api_view([POST])
def logout_view(request):
    return logout(request)

@api_view([PUT])
def authorization_view(request):
    return authorization(request)