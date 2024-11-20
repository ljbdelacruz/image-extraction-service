# boto3_singleton.py
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
load_dotenv()

class S3ClientSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if S3ClientSingleton._instance is None:
            S3ClientSingleton()
        return S3ClientSingleton._instance

    def __init__(self):
        if S3ClientSingleton._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            # Load environment variables from .env file

            # Get AWS credentials from environment variables
            AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
            AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

            # Initialize the S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
            S3ClientSingleton._instance = self

def get_s3_client():
    return S3ClientSingleton.get_instance().s3_client