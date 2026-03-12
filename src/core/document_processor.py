import os
import json
from pathlib import Path
from datetime import datetime
import time
import base64
from typing import Dict, List, Any
import logging

import google.generativeai as genai
from PIL import Image
import fitz
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.processing_result import ProcessingResult
from src.core.image_processor import ImageProcessor
from src.core.prompt_manager import PromptManager
from src.core.document_types import DocumentType

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing class"""
    
    def __init__(self, api_key: str):
        """Initialize with Gemini API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.image_processor = ImageProcessor()
        self.prompt_manager = PromptManager()
        
    def _detect_document_type(self, file_path: str) -> str:
        """Detect document type from file path"""
        path_parts = Path(file_path).parts
        
        if 'driving_license' in path_parts:
            return DocumentType.DRIVING_LICENSE
        elif 'shop_receipts' in path_parts:
            return DocumentType.SHOP_RECEIPT
        elif 'resumes' in path_parts:
            return DocumentType.RESUME
        elif 'marksheets' in path_parts or 'marksheet' in path_parts:
            return DocumentType.MARKSHEET
        else:
            # Fallback: try to detect from filename
            filename = Path(file_path).name.lower()
            if 'license' in filename or 'dl' in filename:
                return DocumentType.DRIVING_LICENSE
            elif 'receipt' in filename or 'invoice' in filename:
                return DocumentType.SHOP_RECEIPT
            elif 'resume' in filename or 'cv' in filename:
                return DocumentType.RESUME
            elif 'marksheet' in filename or 'grade' in filename or 'transcript' in filename:
                return DocumentType.MARKSHEET
            
        return DocumentType.RESUME  # Default fallback
    
    def _convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF pages to images"""
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling
                
                output_path = f"{pdf_path}_page_{page_num}.png"
                pix.save(output_path)
                image_paths.append(output_path)
            
            doc.close()
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path}: {e}")
            return []
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return ""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_gemini(self, prompt: str, image_path: str) -> str:
        """Call Gemini API with retry logic"""
        try:
            # Prepare image
            image = Image.open(image_path)

            # OCR text
            # ocr_text = self.image_processor.extract_text(image_path)
            
            # Call Gemini
            response = self.model.generate_content([prompt, image])
            
            if response.text:
                logger.info("Gemini API call succeeded.")
                return response.text.strip()
            else:
                raise ValueError("Empty response from Gemini")
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _validate_and_clean_json(self, raw_output: str, doc_type: str) -> Dict[str, Any]:
        """Validate and clean JSON output"""
        try:
            # Remove markdown formatting if present
            if raw_output.startswith('```json'):
                raw_output = raw_output[7:-3]
            elif raw_output.startswith('```'):
                raw_output = raw_output[3:-3]
            
            # Parse JSON
            data = json.loads(raw_output)
            
            # Basic validation against schema
            schema = DocumentType.SCHEMAS[doc_type]
            validated_data = {}
            
            for field, field_type in schema.items():
                if field in data:
                    validated_data[field] = data[field]
                else:
                    # Set default values for missing fields
                    if isinstance(field_type, list):
                        validated_data[field] = []
                    else:
                        validated_data[field] = None
            
            return validated_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw output: {raw_output}")
            return self._get_default_schema(doc_type)
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return self._get_default_schema(doc_type)
    
    def _get_default_schema(self, doc_type: str) -> Dict[str, Any]:
        """Get default schema with null values"""
        schema = DocumentType.SCHEMAS[doc_type]
        default_data = {}
        
        for field, field_type in schema.items():
            if isinstance(field_type, list):
                default_data[field] = []
            else:
                default_data[field] = None
        
        return default_data
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], doc_type: str) -> float:
        """Calculate confidence score based on extracted data completeness"""
        schema = DocumentType.SCHEMAS[doc_type]
        total_fields = len(schema)
        filled_fields = sum(1 for value in extracted_data.values() if value is not None and value != "")
        
        return (filled_fields / total_fields) * 100
    
    def process_document(self, file_path: str) -> ProcessingResult:
        """Process a single document"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Detect document type
            doc_type = self._detect_document_type(file_path)
            logger.info(f"Detected document type: {doc_type}")
            
            # Handle PDF files
            if file_path.lower().endswith('.pdf'):
                image_paths = self._convert_pdf_to_images(file_path)
                if not image_paths:
                    raise ValueError("Could not convert PDF to images")
                primary_image = image_paths[0]  # Use first page
            else:
                primary_image = file_path
            
            # Get prompts
            system_prompt = self.prompt_manager.get_system_prompt()
            doc_prompt = self.prompt_manager.get_document_prompt(doc_type, DocumentType.SCHEMAS[doc_type])
            full_prompt = f"{system_prompt}\n\n{doc_prompt}"
            
            # Extract with Gemini
            raw_output = self._call_gemini(full_prompt, primary_image)
            
            # Validate and clean output
            extracted_data = self._validate_and_clean_json(raw_output, doc_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(extracted_data, doc_type)
            
            processing_time = time.time() - start_time
            
            # Clean up temporary files
            if file_path.lower().endswith('.pdf'):
                for temp_path in image_paths:
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            
            return ProcessingResult(
                document_path=file_path,
                document_type=doc_type,
                extracted_data=extracted_data,
                confidence_score=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing {file_path}: {e}")
            
            return ProcessingResult(
                document_path=file_path,
                document_type=self._detect_document_type(file_path),
                extracted_data=self._get_default_schema(self._detect_document_type(file_path)),
                confidence_score=0.0,
                processing_time=processing_time,
                error=str(e),
                validation_status="failed"
            )
    
    def process_batch(self, input_dir: str, output_dir: str) -> List[ProcessingResult]:
        """Process all documents in input directory"""
        results = []
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Find all supported files
        supported_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp']
        files = []
        
        for ext in supported_extensions:
            files.extend(Path(input_dir).rglob(f'*{ext}'))
            files.extend(Path(input_dir).rglob(f'*{ext.upper()}'))
        
        logger.info(f"Found {len(files)} documents to process")
        
        # Process each file
        for file_path in files:
            result = self.process_document(str(file_path))
            results.append(result)
            
            # Save individual result
            output_file = Path(output_dir) / f"{file_path.stem}_result.json"
            with open(output_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Processed {file_path.name}: confidence={result.confidence_score:.1f}%")
        
        # Save batch summary
        summary_file = Path(output_dir) / "batch_summary.json"
        summary = {
            "total_documents": len(results),
            "successful": len([r for r in results if r.error is None]),
            "failed": len([r for r in results if r.error is not None]),
            "average_confidence": sum(r.confidence_score for r in results) / len(results) if results else 0,
            "average_processing_time": sum(r.processing_time for r in results) / len(results) if results else 0,
            "processed_at": datetime.now().isoformat()
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return results