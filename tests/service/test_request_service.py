import unittest
from unittest.mock import patch, MagicMock
from src.service.request_service import create_request, create_image, get_request

class TestRequestService(unittest.TestCase):

    @patch('src.service.request_service.PrismaSingleton.get_instance')
    def test_create_request(self, mock_get_instance):
        # Mock the Prisma instance
        mock_prisma = MagicMock()
        mock_get_instance.return_value = mock_prisma

        # Call the function
        new_request = create_request(custom_id='test_id', base_image='test_image.png')

        # Assertions
        mock_prisma.request.create.assert_called_once_with({
            'data': {
                'id': 'test_id',
                'baseImage': 'test_image.png'
            }
        })

    @patch('src.service.request_service.PrismaSingleton.get_instance')
    def test_create_image(self, mock_get_instance):
        # Mock the Prisma instance
        mock_prisma = MagicMock()
        mock_get_instance.return_value = mock_prisma

        # Call the function
        new_image = create_image(cropped_image_path='test_path', request_id='test_id')

        # Assertions
        mock_prisma.image.create.assert_called_once_with({
            'data': {
                'croppedImagePath': 'test_path',
                'requestId': 'test_id'
            }
        })

    @patch('src.service.request_service.PrismaSingleton.get_instance')
    def test_get_request(self, mock_get_instance):
        # Mock the Prisma instance
        mock_prisma = MagicMock()
        mock_get_instance.return_value = mock_prisma

        # Call the function
        request_record = get_request(request_id='test_id')

        # Assertions
        mock_prisma.request.find_unique.assert_called_once_with(where={'id': 'test_id'}, include={'images': True})

if __name__ == '__main__':
    unittest.main()