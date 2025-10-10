# AI-Powered Enhanced EHR Imaging & Documentation System
# Milestone 1: Data Collection and Preprocessing

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

# Milestone 2: Medical Imaging Enhancement

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


# Milestone 3: Clinical Note Generation & ICD-10 Coding Automation


## 📌 Project Overview

This project aims to reduce the documentation burden for healthcare professionals by leveraging **Generative AI (GenAI)** and **automation**.
The system integrates three core components:

1. **Clinical Note Generation** – Converts structured EHR data into SOAP-format notes.
2. **ICD-10 Coding Automation** – Maps diagnoses to ICD-10 codes using lookup tables or AI.
3. **End-to-End Pipeline** – From raw patient data → AI-generated notes → ICD-10 mapping → final structured output.


 📂 Repository Structure

milestone3_ehr_genai/


├── README.md                     # Project summary, usage, limitations

├── requirements.txt               # Python packages + versions

├── .gitignore                     # Exclude configs, cache, etc.

│

├── data/

│   ├── raw/                       # Synthetic raw patient records & imaging placeholders (non-PHI)

│   ├── processed/                 # Processed inputs for pipeline (CSV/JSON)

│   └── sample_outputs/            # Example outputs (e.g., final_patient_notes_with_icd.csv)

│

├── src/

│   ├── __init__.py

│   ├── preprocess.py              # Data cleaning & formatting

│   ├── note_generation.py         # GenAI / fallback local note generator

│   ├── icd_mapper.py              # ICD mapping logic (lookup + AI-driven)

│   ├── pipeline.py                # End-to-end pipeline orchestration

│   └── utils.py                   # Logging, config helpers

│

├── lookup_tables/

│   └── icd10_lookup.csv           # ICD-10 codes (fallback); source explained in docs

│

├── configs/

│   └── config.yaml                # Configs: paths, API keys (ignored in git), flags (use_api: true/false)

│

├── tests/

│   ├── test_preprocess.py

│   ├── test_icd_mapper.py

│   └── test_pipeline_end_to_end.py

│

└── docs/

    └── milestone3_report.md       # Detailed report: progress, challenges, reproduction steps

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Input

Place patient data in `data/processed/patient_data.csv` with fields:

* `Age, Gender, Symptoms, Diagnosis`

Example:

```csv
Age,Gender,Symptoms,Diagnosis
45,Male,"Fever, Cough, Shortness of breath",Pneumonia
```

### 3. Run Pipeline

```bash
python src/pipeline.py
```

### 4. Check Output

Results are saved in:

```
data/sample_outputs/final_patient_notes_with_icd.csv
```


## 🛠 Features

* AI-generated **SOAP-format notes** using Azure OpenAI / GPT.
* ICD-10 mapping via **lookup table** (fallback) or **AI-driven coding**.
* Modular code (preprocessing, note generation, mapping, pipeline).
* Example datasets included for reproducibility.


## ⚠️ Known Limitations

1. Lookup table covers only common conditions (limited ICD-10 coverage).
2. Multi-diagnosis handling may miss secondary codes.
3. AI notes sometimes vary in length/format.
4. Dependency on Azure API (requires key & internet).

Fallback is always provided:

* If API unavailable → uses local lookup table & simple note generator.



## 📊 Real-World Impact

* Reduces **manual documentation time** for doctors.
* Produces **standardized notes** and **accurate ICD coding**.
* Provides a foundation for future **multi-modal integration** (EHR + imaging + AI coding).


## 👩‍💻 Team Contributions

* **Data Preparation (Milestone 1):** Collected & cleaned imaging + EHR data.
* **Coding (Milestone 2):** Designed ICD-10 lookup + AI mapping.
* **Prototype (Milestone 3):** Built full pipeline integration.
* **Documentation:** Wrote detailed milestone report & README.



