import boto3
from botocore.exceptions import NoCredentialsError
import os
from .boto3_singleton import get_s3_client

# Load environment variables from .env file

# Get AWS credentials from environment variables
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET')

s3_client = get_s3_client()


def upload_single_image(file_obj, bucket_name=AWS_BUCKET_NAME, object_name=None):
    """
    Upload a single image to AWS S3.

    Parameters:
    - file_obj: file-like object, the image file
    - bucket_name: str, name of the S3 bucket
    - object_name: str, S3 object name. If not specified, file_name is used

    Returns:
    - str: URL of the uploaded image
    """
    if object_name is None:
        object_name = file_obj.filename

    try:
        result = s3_client.put_object(            
            Bucket=bucket_name,
            Key=object_name,
            Body=file_obj
        )
        status_code = result['ResponseMetadata']['HTTPStatusCode']
        url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        fileKey=object_name
        return url, fileKey
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        raise
    except NoCredentialsError as e:
        print(f"NoCredentialsError: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def bulk_upload_images(file_paths, bucket_name=AWS_BUCKET_NAME):
    """
    Bulk upload images to AWS S3.

    Parameters:
    - file_paths: list of str, paths to the image files
    - bucket_name: str, name of the S3 bucket

    Returns:
    - list of str: URLs of the uploaded images
    """
    urls = []
    for file_path in file_paths:
        with open(file_path, 'rb') as file_obj:
            url = upload_single_image(file_obj, bucket_name, os.path.basename(file_path))
            if url:
                urls.append(url)
    return urls