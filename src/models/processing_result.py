from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any

@dataclass
class ProcessingResult:
    """Result of document processing"""
    document_path: str
    document_type: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    error: Optional[str] = None
    validation_status: str = "success"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)