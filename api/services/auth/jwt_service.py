import jwt
from datetime import datetime, timezone, timedelta
from decouple import config

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


def _secret() -> str:
    return config("JWT_SECRET_KEY")


def create_access_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, _secret(), algorithm=ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def create_refresh_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, _secret(), algorithm=ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[ALGORITHM])


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
