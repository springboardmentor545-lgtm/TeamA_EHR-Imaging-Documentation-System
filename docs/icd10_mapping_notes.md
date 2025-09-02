# ICD-10 Mapping Notes

This document explains the rationale for selecting ICD-10 codes in the dataset mapping.

## Codes Used

| ICD-10 Code | Definition (WHO ICD-10)                   | Example Diagnoses in Dataset                  |
|-------------|-------------------------------------------|-----------------------------------------------|
| J18.9       | Pneumonia, unspecified organism           | Pneumonia, chest infection                     |
| J20.9       | Acute bronchitis, unspecified             | Bronchitis                                     |
| J98.4       | Other disorders of lung                   | Lung disorder, abnormal chest X-ray            |
| J84.9       | Interstitial pulmonary disease, unspecified | Interstitial lung disease, fibrosis           |
| Z03.8       | Observation for other suspected diseases  | Normal / no abnormality detected               |

## Notes
- Codes were selected based on alignment with ICD-10 official definitions.  
- In case of multiple valid mappings, the most general and widely accepted code was chosen.  
- Ambiguous or unspecified diagnoses (e.g., "Normal") were mapped to **Z03.8**.  
- This ensures consistency across modalities (X-ray and CT) in the dataset.  
