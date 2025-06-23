import json
from src.core.document_types import DocumentType

class PromptManager:
    """Manages prompts for different document types"""
    
    @staticmethod
    def get_system_prompt() -> str:
        return """You are an expert document processing AI specialized in extracting structured data from various document types.
        
            Key Requirements:
            1. Extract ONLY the requested fields with high accuracy
            2. Return valid JSON format without any markdown formatting
            3. Use null for missing information
            4. Maintain data type consistency (strings, numbers, arrays)
            5. Handle edge cases gracefully
            6. Be conservative - if unsure, use null rather than guessing
            7. For dates, use YYYY-MM-DD format
            8. For arrays, ensure proper JSON array structure"""
    
    @staticmethod
    def get_document_prompt(doc_type: str, schema: dict) -> str:
        """Generate document-specific extraction prompt"""
        
        prompts = {
            DocumentType.DRIVING_LICENSE: f"""
                Extract the following information from this driving license:
                {json.dumps(schema, indent=2)}

                Focus on:
                - Full legal name as printed
                - Birth date in YYYY-MM-DD format
                - Complete license number including letters/numbers
                - State that issued the license
                - Expiration date in YYYY-MM-DD format

                Return only valid JSON without markdown formatting.
                """,
            
            DocumentType.SHOP_RECEIPT: f"""
                Extract the following information from this shop receipt:
                {json.dumps(schema, indent=2)}

                Focus on:
                - Store/merchant name (not address)
                - Final total amount as number
                - Purchase date in YYYY-MM-DD format
                - Individual items with names, quantities, and prices
                - Payment method (cash, card, etc.)

                For items array, include each product with quantity and unit price.
                Return only valid JSON without markdown formatting.
                """,
            
            DocumentType.RESUME: f"""
                Extract the following information from this resume/CV:
                {json.dumps(schema, indent=2)}

                Focus on:
                - Complete full name
                - Primary email address
                - Primary phone number
                - Technical and professional skills as array
                - Work experience with company, role, and date ranges
                - Education with institution, degree, and graduation year

                For arrays, ensure proper JSON structure. Use null for missing data.
                Return only valid JSON without markdown formatting.
                """
        }
        
        return prompts.get(doc_type, "Extract structured data from this document.")