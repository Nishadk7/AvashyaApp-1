import os
import uuid
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseStorageService(ABC):
    @abstractmethod
    def save_file(self, file_content: bytes, original_filename: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_reference: str) -> bool:
        pass

    @abstractmethod
    def get_file_url(self, file_reference: str) -> str:
        pass


class LocalStorageService(BaseStorageService):
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_content: bytes, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return unique_filename

    def delete_file(self, file_reference: str) -> bool:
        file_path = os.path.join(self.upload_dir, file_reference)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False

    def get_file_url(self, file_reference: str) -> str:
        return f"/api/files/{file_reference}"


class S3StorageService(BaseStorageService):
    def __init__(self, bucket_name: str, region_name: str = "ap-south-1"):
        import boto3
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = boto3.client("s3", region_name=region_name)

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
        except Exception:
            return False

    def get_file_url(self, file_reference: str, expiration: int = 3600) -> str:
        if not file_reference.startswith("uploads/"):
            return f"/api/files/{file_reference}"
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_reference},
                ExpiresIn=expiration
            )
            return url
        except Exception:
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_reference}"


def get_storage_service() -> BaseStorageService:
    provider = os.getenv("STORAGE_PROVIDER", "").lower()
    bucket_name = os.getenv("S3_BUCKET_NAME", "")
    region_name = os.getenv("AWS_REGION", "ap-south-1")

    if provider == "s3" or bucket_name:
        if not bucket_name:
            return LocalStorageService()
        try:
            return S3StorageService(bucket_name=bucket_name, region_name=region_name)
        except Exception:
            return LocalStorageService()

    return LocalStorageService()
