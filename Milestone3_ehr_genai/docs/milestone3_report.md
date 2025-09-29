 📑 MILESTONE-3 DOCUMENTATION
Project Title: AI-Powered-Enhanced EHR Imaging & Documentation System
Team Name & Members: Team A
-	Samriddhi Tiwary
-	Hima Anjuri
-	Pravalika
-	Rajeswari
-	Dhanasree
-	Sushmasri
-	Shazfa
-	Shobith Reddy
-	Gokula prasath
Course / Semester / Instructor Name: Aryan Khurana
Date of Submission: [29/09/2025]
________________________________________
🔹 Project Vision
Healthcare professionals often spend their time on documentation and administrative tasks. 
Our project aims to reduce this burden by using Generative AI to:
1.	Generate structured clinical notes from raw patient data.
2.	Automate ICD-10 coding for diagnoses.
3.	Build an end-to-end prototype integrating these tasks seamlessly.________________________________________
🔹 Connection with Milestones
•	Milestone 1: Data Collection & Preprocessing
o	Gathered imaging + clinical datasets (EHR, ICD-10).
o	Cleaned, standardized, and prepared datasets for GenAI compatibility.
•	Milestone 2: Data-to-Insights
o	Developed methods to turn structured data into clinical notes.
o	Automated ICD-10 mapping (lookup + AI-driven).
•	Milestone 3: Automation Prototype (This Module)
o	Combined all steps into a working pipeline from raw data → AI note → ICD-10 code → final output.
🔹 Milestone Progression
Milestone 1: Data Collection & Preprocessing
•	Collected medical imaging datasets (CT, MRI, X-ray, Ultrasound).
•	Gathered structured and unstructured EHR data (age, gender, diagnosis, ICD codes).
•	Cleaned, standardized, and labeled data.
•	Ensured privacy by using synthetic or open-source datasets.
Challenge: Ensuring data quality while dealing with unstructured formats and duplicates.
________________________________________
Milestone 2: Data-to-Insights
•	Converted structured patient attributes into clinical documentation format.
•	Designed lookup and AI-driven mapping for ICD-10 coding.
•	Developed logic to handle multiple diagnoses per patient.
Challenge: Maintaining accuracy in ICD-10 mapping and consistency across different cases.
________________________________________
Milestone 3: Automation Prototype (This Module)
Step 1: Prepare Sample Patient Data
•	Since real EHR cannot be used, we created 10+ synthetic cases.
•	Stored as CSV/JSON for reproducibility.
Example:
Age	Gender	Symptoms	Diagnosis
45	Male	Fever, Coughness, Shortness of breath	Pneumonia

________________________________________
Step 2: Clinical Note Generation
•	Used Azure OpenAI (GPT-4/3.5) to generate professional notes.
•	Notes follow SOAP format (Subjective, Objective, Assessment, Plan).
Example AI Output:
•	Patient: 45-year-old male
•	Presenting Complaints: Fever, cough, shortness of breath
•	Assessment: Likely pneumonia
•	Plan: Chest X-ray, antibiotics
Challenge: Ensuring notes are consistent and medically accurate without hallucinations.
________________________________________
Step 3: ICD-10 Coding Automation
•	Option 1 (Lookup): CSV file maps conditions → codes.
•	Option 2 (AI-driven): Ask GPT directly for ICD-10.
Example:
•	Pneumonia → J18.9
•	Hypertension → I10
Challenge: Lookup tables need constant updating; AI sometimes gives multiple/ambiguous codes.
________________________________________
Step 4: Integration (Prototype)
•	Python script connects everything:
1.	Reads patient data.
2.	Calls AI → generates note.
3.	Maps ICD-10 code.
4.	Saves results to output.csv.
Output Example:
Patient	Symptoms	Note generated	ICD-10 
1	Fever, Cough	Patient shows signs of pneumonia..	J18.9
			
________________________________________
Step 5: Documentation & Submission
•	Input files: CSV/JSON of patient records.
•	Code: Python + Azure OpenAI integration.
•	Output: Notes + ICD-10 codes in CSV/JSON.
•	README.md with explanation of workflow, assumptions, and limitations.
________________________________________
🔹 Progress So Far
•	✅ Dummy patient dataset created.
•	✅ Notes successfully generated with Azure GPT.
•	✅ ICD-10 mapping works (lookup + AI).
•	✅ Prototype tested and outputs verified.
________________________________________
🔹 Known Issues
1.	Limited ICD-10 coverage (our lookup table has only common conditions).
2.	Handling multi-diagnosis patients is tricky (AI sometimes misses secondary codes).
3.	AI-generated notes sometimes vary in length and format.
4.	Azure API dependency (internet, API key).
________________________________________
🔹 How to Reproduce
1.	Prepare patient_data.csv with fields: Age, Gender, Symptoms, Diagnosis.
2.	Run clinical_pipeline.py.
3.	Output saved as results/output_notes.csv with:
o	Patient Data
o	AI-Generated Clinical Note
o	ICD-10 Code
________________________________________
🔹 Real-World Impact
•	Doctors spend less time on manual documentation.
•	Hospitals get standardized notes and accurate coding.
•	Lays foundation for multi-modal integration (images + EHR + coding).
________________________________________

🔹 Team Contributions
•	Data Preparation (Milestone 1): Team collected & cleaned imaging + EHR data.
•	Coding (Milestone 2): Team designed lookup + AI ICD mapping.
•	Prototype Integration (Milestone 3): Team built Python script + outputs.
•	Documentation: Prepared detailed workflow, challenges, and progress report.
________________________________________

🌟 Final Summary
This documentation shows our journey from Milestone 1 (Data Collection) → Milestone 2 (Data-to-Insights) → Milestone 3 (Automation Prototype).

We have successfully:
•	Built sample patient datasets.
•	Automated note generation with GenAI.
•	Mapped diagnoses to ICD-10 codes.
•	Integrated everything into a working pipeline.
👉 The project demonstrates not only technical skills but also teamwork, problem-solving, and a strong foundation for future AI-enabled healthcare solutions.

