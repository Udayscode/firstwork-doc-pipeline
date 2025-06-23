import cv2
import numpy as np
import pytesseract
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image preprocessing and OCR"""
    
    def __init__(self):
        # Configure tesseract if needed (uncomment and set path if required)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            return denoised
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    def extract_text(self, image_path: str) -> str:
        """Extract text using OCR"""
        try:
            processed_image = self.preprocess_image(image_path)
            
            # Use pytesseract to extract text with confidence data
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Extract text with confidence filtering
            text_lines = []
            for i in range(len(data['text'])):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()
                if confidence > 50 and text:  # Filter low confidence detections (0-100 scale)
                    text_lines.append(text)
            
            return '\n'.join(text_lines)
            
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return ""