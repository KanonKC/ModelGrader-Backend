import jwt
from datetime import datetime, timezone, timedelta
from api.config import settings

_auth = settings.auth


def create_access_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_auth.access_token_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, _auth.jwt_secret_key, algorithm=_auth.jwt_algorithm)
    return token if isinstance(token, str) else token.decode("utf-8")


def create_refresh_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=_auth.refresh_token_expire_days),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, _auth.jwt_secret_key, algorithm=_auth.jwt_algorithm)
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _auth.jwt_secret_key, algorithms=[_auth.jwt_algorithm])


def verify_access_token(token: str) -> str:
    """Verify access token, return account_id or raise jwt.InvalidTokenError."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Not an access token.")
    return payload["sub"]


def verify_refresh_token(token: str) -> str:
    """Verify refresh token, return account_id or raise jwt.InvalidTokenError."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token.")
    return payload["sub"]
