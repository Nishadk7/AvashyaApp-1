import os
import uuid
import logging
import boto3

logger = logging.getLogger(__name__)

class S3StorageService:
    """
    Production Amazon S3 Storage Service.
    Uploads objects directly to Amazon S3 and generates Zero-Trust S3 Pre-Signed URLs.
    """
    def __init__(self, bucket_name: str = None, region_name: str = None):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "avashya-drop-uploads-2026")
        self.region_name = region_name or os.getenv("AWS_REGION", "ap-south-1")
        self.s3_client = boto3.client("s3", region_name=self.region_name)
        logger.info(f"Initialized Pure Amazon S3 Storage Service (Bucket: {self.bucket_name}, Region: {self.region_name})")

    def save_file(self, file_content: bytes, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        s3_key = f"uploads/{uuid.uuid4().hex}{ext}"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_content
        )
        return s3_key

    def delete_file(self, file_reference: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_reference
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete S3 object {file_reference}: {e}")
            return False

    def get_file_url(self, file_reference: str, expiration: int = 3600) -> str:
        """
        Generates a secure, short-lived Amazon S3 Pre-Signed URL (Zero-Trust pattern).
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_reference},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate S3 Pre-Signed URL for {file_reference}: {e}")
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_reference}"


def get_storage_service() -> S3StorageService:
    bucket_name = os.getenv("S3_BUCKET_NAME", "avashya-drop-uploads-2026")
    region_name = os.getenv("AWS_REGION", "ap-south-1")
    return S3StorageService(bucket_name=bucket_name, region_name=region_name)
