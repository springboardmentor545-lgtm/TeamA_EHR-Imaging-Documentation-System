import pandas as pd
import random

# --- CONFIGURATION ---
OUTPUT_CSV_FILE = "patient_data.csv"
NUMBER_OF_PATIENTS = 10

# --- DATA POOLS FOR RANDOM GENERATION ---
# List of symptom-diagnosis pairs to make the data more realistic
CONDITIONS = [
    {"symptoms": "Fever, persistent cough, body aches", "diagnosis": "Influenza"},
    {"symptoms": "Severe headache, sensitivity to light, nausea", "diagnosis": "Migraine"},
    {"symptoms": "Shortness of breath, wheezing, chest tightness", "diagnosis": "Asthma exacerbation"},
    {"symptoms": "Upper abdominal pain, bloating, indigestion", "diagnosis": "Gastritis"},
    {"symptoms": "Frequent urination, excessive thirst, unexplained weight loss", "diagnosis": "Type 2 Diabetes"},
    {"symptoms": "Joint pain and stiffness, particularly in the morning", "diagnosis": "Rheumatoid Arthritis"},
    {"symptoms": "Consistently high blood pressure readings, occasional headaches", "diagnosis": "Hypertension"},
    {"symptoms": "Symptoms related to renal failure, acute", "diagnosis": "Acute Renal Failure"},
    {"symptoms": "Itchy skin rash, redness, and inflammation", "diagnosis": "Dermatitis"}
]

def create_random_patient_data():
    """Generates and saves a CSV file with random patient data."""
    patient_records = []
    print(f"🤖 Generating {NUMBER_OF_PATIENTS} random patient records...")

    for _ in range(NUMBER_OF_PATIENTS):
        condition = random.choice(CONDITIONS)
        
        patient = {
            "age": random.randint(20, 85),
            "gender": random.choice(["Male", "Female"]),
            "symptoms": condition["symptoms"],
            "diagnosis": condition["diagnosis"]
        }
        patient_records.append(patient)

    # Convert the list of dictionaries to a pandas DataFrame
    patient_df = pd.DataFrame(patient_records)

    
    try:
        patient_df.to_csv(OUTPUT_CSV_FILE, index=False)
        print(f" Successfully created '{OUTPUT_CSV_FILE}' with {NUMBER_OF_PATIENTS} records.")
    except Exception as e:
        print(f" Error saving file: {e}")

if __name__ == "__main__":
    create_random_patient_data()