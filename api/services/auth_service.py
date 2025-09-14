from django.forms.models import model_to_dict
from time import time
from ..models import Account
from ..errors.common import *

# 1757816643.071093
# 1757821551

def verify_token(token):
    """
    Check if user has valid token and not expired
    Return: True/False
    """
    try:
        account = Account.objects.get(token=token)
        account_dict = model_to_dict(account)
        if account_dict['token_expire'] >= time():
            return True
        else:
            return False
    except Account.DoesNotExist:
        return False
    
def getAccountByToken(token):
    """
    Get account from token
    Return: account object
    """
    try:
        account = Account.objects.get(token=token)
        if account.token_expire < time():
            raise InvalidTokenError()
        return account
    except Account.DoesNotExist:
        raise InvalidTokenError()
    except Exception as e:
        raise e