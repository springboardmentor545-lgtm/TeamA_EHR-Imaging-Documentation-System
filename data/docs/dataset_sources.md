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

## 3. CT images
- **Type**: Unstructured Dataset
- **Source**:From kaggle link -> https://www.kaggle.com/datasets/subhajeetdas/iq-othnccd-lung-cancer-dataset-augmented
- **Content**:These images are CT scan slices of lung tissue sourced from Iraqi hospitals, and the dataset has been augmented to increase the number of training samples
- **Purpose**:It provides unstructured visual data for aiding early diagnosis, and enabling integration with structured datasets (EHR, ICD-10).

## 4.MRI images
  - **Type**: Unstructured Dataset
  - **Source**:From kaggle link->https://www.kaggle.com/datasets/navoneel/brain-mri-images-for-brain-tumor-detection
  - **Content**: Contains images with Brain tumors
  - **Purpose**:The Brain MRI dataset is used to train and evaluate AI models for brain tumor detection, enabling classification of normal vs. tumor cases. It supports early diagnosis
