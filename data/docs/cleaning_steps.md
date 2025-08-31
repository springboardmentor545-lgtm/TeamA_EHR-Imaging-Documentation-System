# Data Cleaning and Preprocessing Steps

## 1. Structured Dataset (EHR_cleaned.csv)
- **Initial Check**: Loaded dataset and inspected row/column counts.
- **Duplicate Removal**: Applied `drop_duplicates()` to remove any duplicate rows.
- **Noise Removal**: 
  - Removed extra whitespace.
  - Standardized categorical fields (e.g., gender: "M/F" → "Male/Female").
  - Checked for missing/null values and handled appropriately.
- **Output**: Cleaned structured dataset saved as `EHR_cleaned.csv`.

## 2. Unstructured Dataset (Cynthia PDFs)
- **Source**: 5 PDF files from Cynthia Synthetic EHR dataset.
- **Processing**:
  - Extracted text using `pdfplumber`.
  - Classified lines into **structured (demographics, diagnoses, procedures)** and **unstructured (notes, narratives, discharge summaries)** using keyword matching.
  - Structured sections exported to CSV for analysis.
  - Unstructured notes exported into separate `.txt` files for NLP tasks.
- **Output**:
  - `structured_output/structured_data.csv`
  - `unstructured_output/note_*.txt`
