"""
S3-compatible file storage service (AWS S3 / Cloudflare R2)
"""
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import uuid
from typing import Optional

from app.core.config import settings


def get_s3_client():
    kwargs = {
        "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
        "region_name": settings.S3_REGION,
        "config": Config(signature_version="s3v4"),
    }
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
    return boto3.client("s3", **kwargs)


def _cloud_configured() -> bool:
    """False in local mode (no S3/R2 keys) — callers must skip cloud upload
    instead of letting boto3 hang on IMDS credential lookup."""
    return bool(settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY)


def upload_file(
    file_content: bytes,
    filename: str,
    content_type: str,
    folder: str = "resumes",
) -> Optional[str]:
    """Upload file to S3/R2, return the S3 key"""
    if not _cloud_configured():
        return None
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    key = f"{folder}/{uuid.uuid4()}.{ext}"
    try:
        client = get_s3_client()
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )
        return key
    except Exception as e:
        # Local mode (no S3 keys): skip cloud upload gracefully
        print(f"S3 upload skipped: {e}")
        return None


def upload_pdf_report(file_content: bytes, analysis_id: str) -> Optional[str]:
    """Upload generated PDF report"""
    if not _cloud_configured():
        return None
    key = f"reports/{analysis_id}/report.pdf"
    try:
        client = get_s3_client()
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType="application/pdf",
        )
        return key
    except Exception as e:
        print(f"S3 upload skipped: {e}")
        return None


def get_presigned_url(key: str, expires_in: int = 3600) -> Optional[str]:
    """Generate a presigned URL for downloading a file"""
    try:
        client = get_s3_client()
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        print(f"Presigned URL skipped: {e}")
        return None


def delete_file(key: str) -> bool:
    try:
        client = get_s3_client()
        client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        print(f"S3 delete skipped: {e}")
        return False
