# AI-Powered Enhanced EHR Imaging & Documentation System
## 📌 Project Overview
This project aims to reduce the documentation burden for healthcare professionals by leveraging **Generative AI (GenAI)** and **automation**.
The system integrates three core components:
1. **Clinical Note Generation** – Converts structured EHR data into SOAP-format notes.
2. **ICD-10 Coding Automation** – Maps diagnoses to ICD-10 codes using lookup tables or AI.
3. **End-to-End Pipeline** – From raw patient data → AI-generated notes → ICD-10 mapping → final structured output.
## 📂 Repository Structure
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

    └── milestone3_report.md       # Detailed report: progress, challenges, reproduction step

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




