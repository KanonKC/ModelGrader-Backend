from django.http import HttpResponse
from api.services.auth.jwt_service import REFRESH_TOKEN_EXPIRE_DAYS

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def set_refresh_cookie(response: HttpResponse, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=False,   # set True in production (requires HTTPS)
        samesite="Lax",
        path="/api/auth/token/refresh",
    )


def get_refresh_token_from_cookie(request) -> str | None:
    return request.COOKIES.get(REFRESH_COOKIE_NAME)


def clear_refresh_cookie(response: HttpResponse) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api/auth/token/refresh",
    )
