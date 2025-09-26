import os
import random
import webbrowser
import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


MODEL_NAME = "deepseek/deepseek-chat"
INPUT_FILE = "patient_data.csv"




def generate_clinical_note_with_openrouter(age, gender, symptoms, diagnosis):
    """
    Generate a professional clinical note using OpenRouter API (DeepSeek model).

    Args:
        age (int): Patient's age
        gender (str): Patient's gender
        symptoms (str): Reported symptoms
        diagnosis (str): Diagnosis information

    Returns:
        str: Generated clinical note (or error message)
    """
    if not OPENROUTER_API_KEY:
        error_msg = "[ERROR] OPENROUTER_API_KEY not found in environment or .env file."
        print(error_msg)
        return error_msg

    try:
        prompt = (
            f"You are a clinical documentation assistant. Given the following patient data:\n"
            f"Age: {age}, {gender.capitalize()}\n"
            f"Symptoms: {symptoms}\n"
            f"Diagnosis: {diagnosis}\n\n"
            f"Write a concise, professional clinical note in a standard medical format."
        )

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 250
            }
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error occurred: {http_err}")
        print(f"[ERROR] Response Body: {response.text}")
        return "Error: API request failed with HTTP error."
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return "Error: Could not generate clinical note."


def display_note_in_html(patient_data, clinical_note):
    """
    Display a single clinical note in an HTML page.

    Args:
        patient_data (pd.Series): A series containing one patient's data.
        clinical_note (str): The generated clinical note for the patient.
    """
    age, gender = patient_data['age'], patient_data['gender']
    symptoms, diagnosis = patient_data['symptoms'], patient_data['diagnosis']
    
   
    clean_note = clinical_note.replace('**', '')
    note = clean_note.replace('\n', '<br>')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Clinical Note</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f6fa; margin: 0; padding: 0; }}
            .container {{ background-color: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 30px; max-width: 800px; margin: 40px auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a73e8; font-size: 28px; margin-bottom: 10px; }}
            h2 {{ color: #444; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; margin-top: 25px; }}
            p {{ font-size: 16px; line-height: 1.6; }}
            strong {{ color: #1a73e8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Generated Clinical Note</h1>
            <h2>Patient Information</h2>
            <p><strong>Age:</strong> {age}</p>
            <p><strong>Gender:</strong> {gender.capitalize()}</p>
            <p><strong>Symptoms:</strong> {symptoms}</p>
            <p><strong>Diagnosis:</strong> {diagnosis}</p>
            <h2>Generated Clinical Note</h2>
            <p>{note}</p>
        </div>
    </body>
    </html>
    """
    html_filename = "clinical_note.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n📄 Opening the generated note in '{html_filename}'...")
    webbrowser.open('file://' + os.path.realpath(html_filename))


# ---------------------------
# MAIN SCRIPT
# ---------------------------
def main():
    # Load patient data
    try:
        patient_df = pd.read_csv(INPUT_FILE)
        if patient_df.empty:
            print(f"[ERROR] '{INPUT_FILE}' is empty. Cannot generate a note.")
            return
    except FileNotFoundError:
        print(f"[ERROR] '{INPUT_FILE}' not found. Please create it first.")
        return

    # Check for API key
    if not OPENROUTER_API_KEY:
        print("[FATAL] OPENROUTER_API_KEY is not set. Exiting.")
        return

    print("📝 Selecting one random patient to generate a note...")
    # Select one random patient from the DataFrame
    random_patient = patient_df.sample(n=1).iloc[0]

    print("🔗 Connecting to OpenRouter API to generate a single note...")
    # Generate the note for only that patient
    note = generate_clinical_note_with_openrouter(
        age=random_patient['age'],
        gender=random_patient['gender'],
        symptoms=random_patient['symptoms'],
        diagnosis=random_patient['diagnosis']
    )

    # Check if note generation was successful before displaying
    if "Error:" in note:
        print("\n❌ Failed to generate the clinical note. Please check the error messages above.")
    else:
        print("✅ Note generated successfully!")
        # Display the single generated note in HTML
        display_note_in_html(random_patient, note)


if __name__ == "__main__":
    main()