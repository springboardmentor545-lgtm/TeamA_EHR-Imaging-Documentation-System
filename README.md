Milestone 1: Data Collection and Preprocessing

📌 Objective

The goal of this milestone is to collect, organize, and preprocess medical imaging and clinical (EHR) data to prepare it for downstream AI/GenAI model training and applications.
________________________________________
📂 Tasks Completed

1. Data Collection

•	Medical Imaging Datasets

o	Collected openly available datasets: X-ray, MRI, CT, Ultrasound, DXA

o	Sources: Kaggle, PhysioNet, NIH, and other open repositories.

•	Electronic Health Records (EHR)

o	Gathered structured data: demographics, vitals, lab test results, coded values (ICD/CPT).

o	Gathered unstructured data: patient notes, discharge summaries, and free-text reports.

________________________________________

2. Preprocessing

•	Cleaning

o	Removed duplicates and noisy/unreadable samples.

o	Standardized missing values and normalized units.

•	Labeling

o	Created mappings between imaging samples and corresponding patient metadata.

o	Annotated EHR notes with structured labels (e.g., diagnosis codes, conditions).

•	Standardization

o	Converted images into a uniform format (.png, .jpg, .nii).

o	Tokenized and standardized text data for GenAI compatibility (UTF-8, lowercasing, de-identification).

o	Ensured compliance with privacy and de-identification protocols (HIPAA/GDPR safe).
________________________________________

📊 Output of Milestone 1
Enhancing_EHRs_with_GenAI/
│

├── data/

│   ├── images/


│   │   ├── MRI_001.png
│   │   ├── MRI_002.png
│   │   └── CT_001.png
│   │

│   ├── ehr_notes/
│   │   ├── note_001.txt
│   │   ├── note_002.txt
│   │   └── note_003.txt
│   │

│   ├── mapping.csv
│


├── docs/
│   ├── dataset_sources.md
│   ├── cleaning_steps.md
│   └── challenges.md
│
└── README.md

•	Mapping file linking imaging IDs ↔ EHR records.
