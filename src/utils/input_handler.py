import requests
import tempfile
import os
from typing import List
from pdf2image import convert_from_path
import cv2
import numpy as np

class InputHandler:
    def download_file(self, url: str) -> str:
        """
        Download file from URL to a temporary file.
        Returns the path to the temporary file.
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Infer extension or default to .pdf
        ext = os.path.splitext(url)[1]
        if not ext:
            ext = '.pdf' # Default assumption
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            return tmp_file.name

    def load_pages(self, file_path: str) -> List[np.ndarray]:
        """
        Load file pages as images (numpy arrays).
        Supports PDF and common image formats.
        """
        ext = os.path.splitext(file_path)[1].lower()
        images = []
        
        if ext == '.pdf':
            # Convert PDF to images
            # Note: poppler_path might need to be configured if not in PATH
            pil_images = convert_from_path(file_path)
            for p_img in pil_images:
                # Convert PIL to cv2 (RGB -> BGR)
                open_cv_image = np.array(p_img) 
                open_cv_image = open_cv_image[:, :, ::-1].copy() 
                images.append(open_cv_image)
        else:
            # Assume it's an image
            img = cv2.imread(file_path)
            if img is not None:
                images.append(img)
                
        return images
