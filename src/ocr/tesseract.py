import pytesseract
import numpy as np
from typing import List, Dict, Any
from .engine import OCREngine

class TesseractOCR(OCREngine):
    """
    Tesseract OCR implementation.
    """

    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract raw text using Tesseract.
        """
        return pytesseract.image_to_string(image)

    def extract_data(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract detailed data using Tesseract.
        """
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        results = []
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0: # Filter out low confidence/empty results
                results.append({
                    'text': data['text'][i],
                    'conf': float(data['conf'][i]),
                    'bbox': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                })
        return results

    def detect_tables(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Table detection is not natively supported by Tesseract.
        This is a placeholder or could use a heuristic approach.
        """
        # TODO: Implement heuristic table detection or integrate with LayoutParser
        return []
