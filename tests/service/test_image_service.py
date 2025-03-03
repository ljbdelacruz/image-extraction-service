import unittest
from unittest.mock import patch, MagicMock, mock_open
from PIL import Image
from io import BytesIO
import os
import uuid
from src.service.image_service import image_background_remover

class TestImageService(unittest.TestCase):

    @patch('src.service.image_service.remove')
    @patch('src.service.image_service.os.makedirs')
    @patch('src.service.image_service.os.path.exists')
    @patch('src.service.image_service.cv2.imread')
    @patch('src.service.image_service.cv2.imencode')
    @patch('builtins.open', new_callable=mock_open)
    def test_image_background_remover(self, mock_open, mock_imencode, mock_imread, mock_exists, mock_makedirs, mock_remove):
        # Mock the input image
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Mock the remove function
        mock_remove.return_value = img

        # Mock os.path.exists to return False initially
        mock_exists.return_value = False

        # Mock os.makedirs to do nothing
        mock_makedirs.return_value = None

        # Mock cv2.imread to return a numpy array
        mock_imread.return_value = MagicMock()

        # Mock cv2.imencode to return a buffer
        mock_imencode.return_value = (True, b'encoded_image')

        # Call the function
        file_obj, unique_filename, output_path = image_background_remover(img, 'test_path', 'test_output_dir')

        # Assertions
        self.assertIsInstance(file_obj, BytesIO)
        self.assertTrue(unique_filename.startswith('test_path/'))
        self.assertTrue(output_path.startswith('test_output_dir/'))

if __name__ == '__main__':
    unittest.main()