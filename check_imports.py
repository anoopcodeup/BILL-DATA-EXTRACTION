try:
    import numpy
    print("numpy imported")
except ImportError as e:
    print(f"numpy failed: {e}")

try:
    import cv2
    print("cv2 imported")
except ImportError as e:
    print(f"cv2 failed: {e}")

try:
    import pytesseract
    print("pytesseract imported")
except ImportError as e:
    print(f"pytesseract failed: {e}")

try:
    import anthropic
    print("anthropic imported")
except ImportError as e:
    print(f"anthropic failed: {e}")
