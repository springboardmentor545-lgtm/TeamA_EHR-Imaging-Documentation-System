# Dataset Sources

## 1. Cynthia Synthetic EHR Dataset
- **Type**: Synthetic, de-identified  
- **Format**: 5 PDF files simulating Electronic Health Records  
- **Content**: Includes both **structured data** (demographics, diagnoses, procedures, medications) and **unstructured data** (physician notes, discharge summaries, narratives).  
- **Purpose**: Used for testing and prototyping structured/unstructured EHR workflows without handling real patient data.  

## 2. EHR_cleaned.csv
- **Type**: Cleaned structured dataset  
- **Source**: Derived from the original Cynthia dataset by preprocessing and standardization.  
- **Content**: Patient-level structured attributes (age, sex, diagnoses, ICD codes, etc.) cleaned and deduplicated.  
- **Purpose**: Used for structured data tasks such as ICD-10 coding, classification, and analytics.  
