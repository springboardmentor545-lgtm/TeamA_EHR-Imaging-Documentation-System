import pandas as pd

# Load your patient data (output from Step 2)
df = pd.read_excel("patient_notes_with_generated_notes.xlsx")

# Load ICD-10 lookup table
lookup_df = pd.read_csv("icd10_lookup.csv")

# Function to get ICD-10 code
def get_icd10_code(diagnosis):
match = lookup_df[lookup_df["Diagnosis"].str.lower() == diagnosis.lower()]
if not match.empty:
return match["ICD-10 Code"].values[0]
return "Unknown"

# Apply function to add ICD-10 codes
df["ICD-10 Code"] = df["Diagnosis"].apply(get_icd10_code)

# Save final dataset
df.to_excel("final_patient_notes_with_the_icd.xlsx", index=False)

print("✅ ICD-10 coding automation completed!")
