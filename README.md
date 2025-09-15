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

Milestone 2: Medical Imaging Enhancement

📌 Project Overview

This project focuses on enhancing medical images (MRI, CT, X-ray) using Generative AI and classical deep learning models. The goal is to improve image clarity, denoise scans, and provide healthcare professionals with diagnostic-quality visuals.

Milestone 2 covers implementation, experimentation, and evaluation of image enhancement techniques.
📂 Folder Structure

Milestone2/

│|    

|├── Documentation   # Reports, milestone documentation, write-ups

|├── Presentation    # PPT files summarizing the milestone

|├── Projectfile     # Source code, preprocessing, and model scripts

|├── Resources       # Reference papers, notes, datasets (links if large)

|└── Results         # Enhanced vs original images, zipped outputs

✅ Steps Completed in Milestone 2
1. Dataset Preparation

Collected MRI, CT, and X-ray images.

Selected ~20–50 images for testing enhancement.

2. Preprocessing

Standardized formats: .png, resized to 256x256.

Normalized pixel values to range 0.0 – 1.0.

Created train/test split.

3. Enhancement Techniques Applied

Classical Deep Models: DnCNN, EDSR, SRCNN.

Generative AI-based: API-based denoising & upscaling.

OpenCV Methods: Backup sharpening & noise reduction.

4. Validation

Compared before vs. after images.

Metrics used: PSNR (Peak Signal-to-Noise Ratio), SSIM (Structural Similarity Index).

Results stored in /Results folder.

5. Challenges Faced

Slow CPU training → shifted to Colab GPU.

Some models produced blurry outputs.

Handling large result sets (~100 images) was difficult.

Used OpenCV methods when deep models underperformed.

📊 Results

Enhanced images show better clarity and sharpness.

Visual evaluation proved more reliable than metrics (due to limited ground-truth HQ images).

Hybrid approach (Classical + GenAI) achieved the best overall results.
