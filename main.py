import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from backup_sql import create_backup
import os

load_dotenv()

s3_bucket = os.getenv("S3_BUCKET")
profile_name = os.getenv("AWS_PROFILE_NAME")

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    session = boto3.Session(profile_name=profile_name)

    # Upload the file
    s3_client = session.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.info(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True

file_to_upload = create_backup()

upload_file(file_to_upload, s3_bucket)