# Multimodal Document Extraction Pipeline
This tool extracts data from various files in a personal database. It uses AI to turn images and documents into organized, searchable information.

### Core Features
- Intelligent Image Pre-processing: Uses OpenCV to handle real-world noise like shadows, low contrast, and blur to ensure high-quality text extraction.
- Multimodal Text Recognition: Combines Tesseract OCR for text detection with AI-driven visual reasoning to understand layouts and graphics.
- Modular Architecture: Built with a "plugin" style structure to easily handle new file formats (Word, PowerPoint, PDF) by swapping small processing modules.
- Data Structuring: Automatically maps raw findings into clean, validated JSON files that are ready for any local database.

### Technical Setup
```
# Enter the folder
cd multimodal-doc-pipeline

# Set up the environment
python -m venv venv
source venv/bin/activate

# Install the tools
pip install -r requirements.txt
```
### Usage
Process One File
Run the pipeline on a single document by pointing to its location:

```
python3 -m src.main \
  --api-key YOUR_API_KEY \
  --input ./data/Resume \
  --output ./outputs/new_resume_results \
  --single ./data/Resume/50583715-3716.jpg
```
### Process Everything
To process all documents in a folder at once:

```
python3 -m src.main --api-key YOUR_API_KEY --input ./data --output ./outputs
```
Notes
- Simple Logic: The system is modular, making it easy to add new types of documents.
- Tracking: All steps are recorded in document_processor.log for troubleshooting.
- Security Goal: While this version uses an API for testing, the structure is built to move toward local processing to keep all user data private and secure.
