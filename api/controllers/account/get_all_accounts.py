from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from django.db.models import Q


def get_all_accounts(request):

    # get search query
    search = request.GET.get('search','')

    accounts = Account.objects.all()

    if search != '':
        accounts = accounts.filter(
            Q(username__icontains=search) | Q(account_id__icontains=search) | Q(email__icontains=search)
        ).distinct()

    serialize = AccountSecureSerializer(accounts,many=True)
    return Response({
        "accounts": serialize.data
    },status=status.HTTP_200_OK)