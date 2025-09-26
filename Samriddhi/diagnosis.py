

import csv
import openai
import os
import openai

# ---------------- CONFIG ----------------
openai.api_key = ""

INPUT_FILE = "C:/Users/samri/cod/TeamA_EHR-Imaging-Documentation-System/Samriddhi/patient_data.csv"
OUTPUT_FILE = "C:/Users/samri/cod/TeamA_EHR-Imaging-Documentation-System/Samriddhi/patients_output.csv"

# Simple ICD-10 lookup table
icd_lookup = {
    "Pneumonia": "J18.9",
    "Diabetes": "E11.9",
    "Hypertension": "I10",
    "Migraine": "G43.9",
    "Asthma": "J45.9",
    "COVID-19": "U07.1",
    "Bronchitis": "J20.9",
    "Heart Failure": "I50.9",
    "Chronic Kidney Disease": "N18.9",
    "Anemia": "D64.9",
    "Stroke": "I63.9",
    "Influenza": "J10.1",
    "Depression": "F32.9",
    "Anxiety": "F41.9",
    "Osteoarthritis": "M19.9",
    "Gastroenteritis": "A09",
    "Appendicitis": "K35.9",
    "Epilepsy": "G40.9",
    "Hyperthyroidism": "E05.9",
    "Hypothyroidism": "E03.9"
}


# ---------------- FUNCTIONS ----------------
def ask_gpt(prompt, max_tokens=200):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0
    )
    return response["choices"][0]["message"]["content"].strip()

def predict_diagnosis(age, gender, symptoms):
    prompt = f"Patient: {age}-year-old {gender}\nSymptoms: {symptoms}\nSuggest the most likely diagnosis in 1-3 words only."
    return ask_gpt(prompt, max_tokens=20)

def generate_clinical_note(age, gender, symptoms, diagnosis):
    prompt = f"Patient: {age}-year-old {gender}\nSymptoms: {symptoms}\nDiagnosis: {diagnosis}\nWrite a structured clinical note with sections:\n- Patient\n- Presenting Complaints\n- Assessment\n- Plan"
    return ask_gpt(prompt, max_tokens=200)

def get_icd10_code(diagnosis):
    if diagnosis in icd_lookup:
        return icd_lookup[diagnosis]
    prompt = f'Given the diagnosis "{diagnosis}", suggest the most appropriate ICD-10 code.'
    return ask_gpt(prompt, max_tokens=20)

# ---------------- MAIN ----------------
def main():
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 2:  # only read first 2 rows for testing
                break

            print(f"Processing patient {i+1}...")
            age = row["age"]
            gender = row["gender"]
            symptoms = row["symptoms"]
            diagnosis = row.get("diagnosis", "").strip()

            if not diagnosis:
                print("  Predicting diagnosis...")
                diagnosis = predict_diagnosis(age, gender, symptoms)
                print(f"  Diagnosis predicted: {diagnosis}")

            print("  Generating clinical note...")
            note = generate_clinical_note(age, gender, symptoms, diagnosis)
            print("  Note generated.")

            icd_code = get_icd10_code(diagnosis)
            print(f"  ICD-10 code: {icd_code}\n")

            results.append({
                "age": age,
                "gender": gender,
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "clinical_note": note,
                "icd10_code": icd_code
            })

    # Save output
    fieldnames = ["age", "gender", "symptoms", "diagnosis", "clinical_note", "icd10_code"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Done! Processed {len(results)} patients. Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()