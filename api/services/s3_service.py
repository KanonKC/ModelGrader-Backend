import boto3
from botocore.exceptions import BotoCoreError, ClientError
from api.config import settings
from api.utility import generate_random_string

_s3 = boto3.client(
    "s3",
    region_name=settings.s3.region,
    aws_access_key_id=settings.s3.access_key,
    aws_secret_access_key=settings.s3.secret_key,
)


def upload_pdf(file, filename_base: str) -> str:
    """Upload a PDF file object to S3 and return the S3 key."""
    key = f"{settings.s3.pdf_prefix}{filename_base}_{generate_random_string()}.pdf"
    try:
        _s3.upload_fileobj(
            file,
            settings.s3.bucket_name,
            key,
            ExtraArgs={"ContentType": "application/pdf"},
        )
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 upload failed: {e}") from e
    return key


def delete_pdf(key: str) -> None:
    """Delete a PDF from S3 by key. Silently ignores missing keys."""
    try:
        _s3.delete_object(Bucket=settings.s3.bucket_name, Key=key)
    except (BotoCoreError, ClientError):
        pass


def get_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a temporary presigned URL for a PDF key."""
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3.bucket_name, "Key": key},
        ExpiresIn=expires_in,
    )
