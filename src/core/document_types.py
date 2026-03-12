class DocumentType:
    """Document type definitions and schemas"""
    
    DRIVING_LICENSE = "driving_license"
    SHOP_RECEIPT = "shop_receipt"
    RESUME = "resume"
    MARKSHEET = "marksheet"
    
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
            "total_amount_without_tax": "float",
            "total_amount": "float",
            "tax": "float",
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
        },
        MARKSHEET: {
            "student_name": "string",
            "roll_number": "string",
            "institution": "string",
            "exam_name": "string",
            "exam_date": "YYYY-MM-DD",
            "subjects": [{"name": "string", "marks_obtained": "float", "maximum_marks": "float", "grade": "string"}],
            "total_marks": "float",
            "percentage": "float",
            "result": "string"
        }
    }