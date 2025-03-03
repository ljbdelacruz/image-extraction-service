import unittest
from unittest.mock import patch, MagicMock
from src.service.upload_s3 import upload_single_image
import os

class TestUploadS3(unittest.TestCase):

    @patch('src.service.upload_s3.s3_client.put_object')
    def test_upload_single_image(self, mock_put_object):
        # Mock the S3 put_object response
        mock_put_object.return_value = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }

        # Mock file object
        file_obj = MagicMock()
        file_obj.filename = 'test_image.png'

        # Set the environment variable for the S3 bucket name
        os.environ['AWS_BUCKET_NAME'] = 'laineltestbucket'

        # Call the function
        url, file_key = upload_single_image(file_obj, object_name='test_image.png')

        # Assertions
        self.assertEqual(url, 'https://laineltestbucket.s3.amazonaws.com/test_image.png')
        self.assertEqual(file_key, 'test_image.png')

if __name__ == '__main__':
    unittest.main()