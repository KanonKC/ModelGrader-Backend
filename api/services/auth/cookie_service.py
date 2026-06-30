from django.http import HttpResponse
from api.config import settings

_auth = settings.auth


def set_refresh_cookie(response: HttpResponse, refresh_token: str) -> None:
    response.set_cookie(
        key=_auth.refresh_cookie_name,
        value=refresh_token,
        max_age=_auth.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=_auth.refresh_cookie_secure,
        samesite=_auth.refresh_cookie_samesite,
        path="/api/auth/token/refresh",
    )


def get_refresh_token_from_cookie(request) -> str | None:
    return request.COOKIES.get(_auth.refresh_cookie_name)


def clear_refresh_cookie(response: HttpResponse) -> None:
    response.delete_cookie(
        key=_auth.refresh_cookie_name,
        path="/api/auth/token/refresh",
    )
