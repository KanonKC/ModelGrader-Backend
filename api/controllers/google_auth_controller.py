import requests as http_requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decouple import config

from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
from api.models import Account
from api.constant import POST
from api.services.auth.jwt_service import create_access_token, create_refresh_token

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def _exchange_code_for_token(code: str, code_verifier: str, redirect_uri: str) -> dict:
    payload = {
        "client_id": config("GOOGLE_CLIENT_ID"),
        "client_secret": config("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    resp = http_requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_google_userinfo(access_token: str) -> dict:
    resp = http_requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _get_or_create_account(email: str) -> Account:
    try:
        return Account.objects.get(email=email)
    except Account.DoesNotExist:
        username_base = email.split("@")[0]
        username = username_base
        counter = 1
        while Account.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        return Account.objects.create(email=email, username=username, password="")


def _build_jwt_response(account: Account) -> dict:
    return {
        "access_token": create_access_token(account.account_id),
        "refresh_token": create_refresh_token(account.account_id),
        "account_id": account.account_id,
        "username": account.username,
        "email": account.email,
    }


@api_view([POST])
def google_callback(request):
    try:
        code = request.data.get("code")
        code_verifier = request.data.get("code_verifier")
        redirect_uri = request.data.get("redirect_uri")

        if not code or not code_verifier or not redirect_uri:
            return Response({"error": "Missing required fields."}, status=400)

        token_data = _exchange_code_for_token(code, code_verifier, redirect_uri)
        user_info = _get_google_userinfo(token_data["access_token"])

        email = user_info.get("email")
        if not email:
            return Response({"error": "Could not retrieve email from Google."}, status=400)

        account = _get_or_create_account(email)
        return Response(_build_jwt_response(account), status=200)

    except GraderException as ge:
        return ge.django_response()
    except http_requests.HTTPError as e:
        return Response({"error": f"Google API error: {str(e)}"}, status=502)
    except Exception as e:
        print("Error", e)
        return InternalServerError(e).django_response()
