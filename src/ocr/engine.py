from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class OCREngine(ABC):
    """
    Abstract Base Class for OCR Engines.
    """

    @abstractmethod
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract raw text from an image.
        """
        pass

    @abstractmethod
    def extract_data(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract detailed data (text, bounding boxes, confidence) from an image.
        Expected return format: List of dicts with keys:
        - 'text': str
        - 'conf': float (0-100)
        - 'bbox': tuple (x, y, w, h)
        """
        pass

    @abstractmethod
    def detect_tables(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect tables in the image.
        Returns a list of detected tables with their bounding boxes and structure.
        """
        pass
