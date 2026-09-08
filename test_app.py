import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from app import pdf_to_images, images_to_pdf

class TestApp(unittest.TestCase):
    @patch("app.fitz")
    def test_pdf_to_images_closes_doc(self, mock_fitz):
        # Setup mock doc
        mock_doc = MagicMock()
        mock_fitz.open.return_value = mock_doc
        mock_doc.__len__.return_value = 0 # 0 pages so loop doesn't run

        pdf_to_images("dummy.pdf", "png", "dummy_dir")

        mock_doc.close.assert_called_once()

    @patch("app.fitz")
    def test_pdf_to_images_closes_doc_on_error(self, mock_fitz):
        # Setup mock doc
        mock_doc = MagicMock()
        mock_fitz.open.return_value = mock_doc
        mock_doc.__len__.side_effect = Exception("Some error")

        with self.assertRaises(Exception):
            pdf_to_images("dummy.pdf", "png", "dummy_dir")

        mock_doc.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
