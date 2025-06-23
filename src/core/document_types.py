class DocumentType:
    """Document type definitions and schemas"""
    
    DRIVING_LICENSE = "driving_license"
    SHOP_RECEIPT = "shop_receipt"
    RESUME = "resume"
    
    SCHEMAS = {
        DRIVING_LICENSE: {
            "name": "string",
            "date_of_birth": "YYYY-MM-DD",
            "license_number": "string",
            "issuing_state": "string",
            "expiry_date": "YYYY-MM-DD"
        },
        SHOP_RECEIPT: {
            "merchant_name": "string",
            "total_amount": "float",
            "date_of_purchase": "YYYY-MM-DD",
            "items": [{"name": "string", "quantity": "int", "price": "float"}],
            "payment_method": "string"
        },
        RESUME: {
            "full_name": "string",
            "email": "string",
            "phone_number": "string",
            "skills": ["string"],
            "work_experience": [{"company": "string", "role": "string", "dates": "string"}],
            "education": [{"institution": "string", "degree": "string", "graduation_year": "int"}]
        }
    }