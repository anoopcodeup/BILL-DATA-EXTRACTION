import cv2
import numpy as np

class ImagePreprocessor:
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing to improve OCR accuracy.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to handle varying lighting/shadows
        # This creates a binary image
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise (optional, can be slow)
        # denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return binary
