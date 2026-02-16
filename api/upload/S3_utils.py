from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
import logging

from starlette import status

from ..config import get
from ..error_constant import ErrorConstants

s3_client = boto3.client(
    "s3",
    aws_access_key_id=get("AWS_ACCESS_KEY"),
    aws_secret_access_key=get("AWS_SECRET_KEY"),
    region_name=get("AWS_REGION")

)


def upload_file(bucket_name: str, s3_key: str, file: UploadFile) -> str:
    try:
        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={
                "ContentType": file.content_type,
                "ExpectedBucketOwner": get("AWS_BUCKET_OWNER")
            }
        )
        return s3_key
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.FAILED_TO_UPLOAD_FILE_TO_S3)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.AN_UNEXPECTED_ERROR_OCCURRED)


def upload_bytes(bucket_name: str, s3_key: str, file: BytesIO, content_type: str) -> str:
    try:
        s3_client.upload_fileobj(
            Fileobj=file,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={
                "ContentType": content_type,
                "ExpectedBucketOwner": get("AWS_BUCKET_OWNER")
            }
        )
        return s3_key
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.FAILED_TO_UPLOAD_FILE_TO_S3)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.AN_UNEXPECTED_ERROR_OCCURRED)


def generate_presigned_access_url(bucket_name: str, s3_key: str):
    if isinstance(s3_key, str) and s3_key.strip():
        # Generate a presigned URL for uploading an object
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key
            },
            ExpiresIn=3600
        )
        return presigned_url
    return ""


def delete_file(file_path: str):
    try:
        s3_client.delete_object(
            Bucket=get("AWS_BUCKET_NAME"), 
            Key=file_path,
            ExpectedBucketOwner=get("AWS_BUCKET_OWNER")
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchKey':
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ErrorConstants.FAILED_TO_DELETE_FILE)
        return False

def download_file_from_s3(bucket_name: str, s3_key: str) -> BytesIO:
    try:
        file_obj = BytesIO()
        s3_client.download_fileobj(
            Bucket=bucket_name,
            Key=s3_key,
            Fileobj=file_obj,
            ExtraArgs={'ExpectedBucketOwner': get("AWS_BUCKET_OWNER")}
        )
        file_obj.seek(0)  # Reset pointer to beginning for reading
        logging.info(f"Successfully downloaded {s3_key} from S3")
        return file_obj
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NoSuchKey':
            logging.error(f"File not found in S3: {s3_key}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorConstants.FILE_NOT_FOUND
            )
        else:
            logging.error(f"Failed to download file from S3: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorConstants.FAILED_TO_DOWNLOAD_FILE_FROM_S3
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorConstants.AN_UNEXPECTED_ERROR_OCCURRED_WHILE_DOWNLOADING_FILE
        )