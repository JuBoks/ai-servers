import os
import boto3
import uuid
from botocore.client import Config
from fastapi import UploadFile

BUCKET_NAME = os.environ["BUCKET_NAME"]
S3_REGION = os.environ["S3_REGION"]

s3 = boto3.client("s3")


def upload_image(serial_number, file: UploadFile):
    file_extension = file.filename.split(".")[-1]
    directory = os.environ[f"{serial_number}_S3"]
    key = f"{directory}/{uuid.uuid4()}.{file_extension}"
    ExtraArgs = {
        "ContentType": file.content_type,
        "ContentDisposition": "inline",
    }
    result = s3.upload_fileobj(file.file, BUCKET_NAME, key, ExtraArgs=ExtraArgs)
    return f"https://{BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}"
