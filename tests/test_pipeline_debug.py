import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock missing dependencies
sys.modules['pytesseract'] = MagicMock()
sys.modules['anthropic'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pdf2image'] = MagicMock()

import numpy as np
# Fix import path for running as script
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline.core import ExtractionPipeline

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ExtractionPipeline()
        self.pipeline.ocr = MagicMock()
        self.pipeline.llm = MagicMock()
        self.pipeline.input_handler = MagicMock()
        self.pipeline.preprocessor = MagicMock()

    def test_pipeline_flow(self):
        try:
            # Mock Input Handler
            self.pipeline.input_handler.download_file.return_value = "dummy.pdf"
            self.pipeline.input_handler.load_pages.return_value = [np.zeros((100, 100, 3), dtype=np.uint8)]
            
            # Mock Preprocessor
            self.pipeline.preprocessor.preprocess.return_value = np.zeros((100, 100), dtype=np.uint8)

            # Mock OCR output
            self.pipeline.ocr.extract_data.return_value = []
            self.pipeline.ocr.extract_text.return_value = "Item 1 10.00"
            
            # Mock LLM output
            self.pipeline.llm.reconstruct_table.return_value = [
                {"item_name": "Item 1", "item_rate": 10.0, "item_quantity": 1, "item_amount": 10.0}
            ]
            
            # Run pipeline
            result = self.pipeline.process_url("http://example.com/bill.pdf")
            
            print("Result:", result)
            
            # Verify
            self.assertEqual(len(result['items']), 1)
            self.assertEqual(result['items'][0]['item_name'], "Item 1")
            self.assertEqual(result['items'][0]['page_number'], 1)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Test failed with exception: {e}")
            raise e

if __name__ == '__main__':
    unittest.main()
