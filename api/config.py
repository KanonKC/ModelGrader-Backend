from decouple import AutoConfig

_env = AutoConfig()


class DatabaseConfig:
    name: str     = _env("DATABASE_NAME")
    user: str     = _env("DATABASE_USER")
    password: str = _env("DATABASE_PASSWORD")
    host: str     = _env("DATABASE_HOST")
    port: str     = _env("DATABASE_PORT", default="5432")


class AuthConfig:
    token_lifetime_seconds: int     = int(_env("TOKEN_LIFETIME_SECOND", default="86400"))
    jwt_secret_key: str             = _env("JWT_SECRET_KEY")
    jwt_algorithm: str              = "HS256"
    access_token_expire_minutes: int  = 15
    refresh_token_expire_days: int    = 7
    refresh_cookie_name: str        = "refresh_token"
    refresh_cookie_secure: bool     = False   # set True in production (HTTPS required)
    refresh_cookie_samesite: str    = "Lax"


class GoogleConfig:
    client_id: str     = _env("GOOGLE_CLIENT_ID")
    client_secret: str = _env("GOOGLE_CLIENT_SECRET")
    token_url: str     = "https://oauth2.googleapis.com/token"
    userinfo_url: str  = "https://www.googleapis.com/oauth2/v3/userinfo"


class S3Config:
    bucket_name: str  = _env("AWS_S3_BUCKET_NAME")
    region: str       = _env("AWS_S3_REGION", default="ap-southeast-1")
    access_key: str   = _env("AWS_ACCESS_KEY_ID")
    secret_key: str   = _env("AWS_SECRET_ACCESS_KEY")
    pdf_prefix: str   = _env("AWS_S3_PDF_PREFIX", default="problem-pdfs/")


class AppConfig:
    frontend_url: str = _env("FRONTEND_URL")
    db = DatabaseConfig()
    auth = AuthConfig()
    google = GoogleConfig()
    s3 = S3Config()


# Singleton — import this everywhere instead of reading .env directly
settings = AppConfig()
