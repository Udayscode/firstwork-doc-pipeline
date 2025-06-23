#!/usr/bin/env python3
"""
FirstWork Document Processing System CLI
"""
import argparse
from pathlib import Path
import json
from src.utils.logging_config import configure_logging
from src.core.document_processor import DocumentProcessor
from src.models.processing_result import ProcessingResult

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="FirstWork Document Processing System")
    parser.add_argument("--api-key", required=True, help="Google Gemini API key")
    parser.add_argument("--input", required=True, help="Input directory containing documents")
    parser.add_argument("--output", required=True, help="Output directory for results")
    parser.add_argument("--single", help="Process single file instead of batch")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    configure_logging(verbose=args.verbose)
    
    # Initialize processor
    processor = DocumentProcessor(args.api_key)
    
    if args.single:
        # Process single file
        result = processor.process_document(args.single)
        output_file = Path(args.output) / f"{Path(args.single).stem}_result.json"
        Path(args.output).mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        
        print(f"Processed {args.single}")
        print(f"Confidence: {result.confidence_score:.1f}%")
        print(f"Output: {output_file}")
    else:
        # Process batch
        results = processor.process_batch(args.input, args.output)
        
        print(f"\nBatch Processing Complete!")
        print(f"Total documents: {len(results)}")
        print(f"Successful: {len([r for r in results if r.error is None])}")
        print(f"Failed: {len([r for r in results if r.error is not None])}")
        print(f"Average confidence: {sum(r.confidence_score for r in results) / len(results):.1f}%")
        print(f"Results saved to: {args.output}")

if __name__ == "__main__":
    main()