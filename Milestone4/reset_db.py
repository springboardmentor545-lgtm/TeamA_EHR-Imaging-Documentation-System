import sqlite3
import os

def reset_database():
    """Completely reset the database"""
    if os.path.exists('cardiac_clinic.db'):
        os.remove('cardiac_clinic.db')
        print("✅ Old database deleted")
    
    # Recreate database with correct schema
    conn = sqlite3.connect('cardiac_clinic.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            patient_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE patients (
            patient_id TEXT PRIMARY KEY NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE patient_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            modality TEXT NOT NULL,
            folder_path TEXT NOT NULL,
            num_slices INTEGER NOT NULL,
            study_date TEXT NOT NULL,
            ward_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            modality TEXT NOT NULL,
            condition_diagnosed TEXT NOT NULL,
            icd10_code TEXT NOT NULL,
            image_features TEXT NOT NULL,
            findings TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            clinical_report TEXT NOT NULL,
            formatted_report TEXT NOT NULL,
            generated_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (generated_by) REFERENCES users (id)
        )
    ''')
    
    # Insert predefined medical staff with proper password hashing
    import hashlib
    def make_hashes(password):
        return hashlib.sha256(str.encode(password)).hexdigest()
    
    predefined_staff = [
        # Administrators
        ('admin', make_hashes('admin123'), 'Administrator', 'System Administrator', 'admin@cardiacclinic.com', None),
        ('director', make_hashes('director123'), 'Administrator', 'Hospital Director', 'director@cardiacclinic.com', None),
        
        # Doctors
        ('dr_smith', make_hashes('smith123'), 'Doctor', 'Dr. John Smith', 'dr.smith@cardiacclinic.com', None),
        ('dr_jones', make_hashes('jones123'), 'Doctor', 'Dr. Sarah Jones', 'dr.jones@cardiacclinic.com', None),
        ('dr_wilson', make_hashes('wilson123'), 'Doctor', 'Dr. Michael Wilson', 'dr.wilson@cardiacclinic.com', None),
        
        # Technicians
        ('tech_davis', make_hashes('davis123'), 'Technician', 'Robert Davis', 'tech.davis@cardiacclinic.com', None),
        ('tech_garcia', make_hashes('garcia123'), 'Technician', 'Maria Garcia', 'tech.garcia@cardiacclinic.com', None),
        ('tech_lee', make_hashes('lee123'), 'Technician', 'David Lee', 'tech.lee@cardiacclinic.com', None),
    ]
    
    for staff in predefined_staff:
        username, password, role, full_name, email, patient_id = staff
        c.execute('''
            INSERT INTO users (username, password, role, full_name, email, patient_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, role, full_name, email, patient_id))
    
    # Load patient data from master_metadata.csv if available
    try:
        import pandas as pd
        df = pd.read_csv('master_metadata.csv')
        if not df.empty:
            # Insert unique patients
            unique_patients = df[['Patient_ID', 'Age', 'Gender']].drop_duplicates()
            for _, patient in unique_patients.iterrows():
                c.execute('INSERT OR IGNORE INTO patients (patient_id, age, gender) VALUES (?, ?, ?)',
                         (patient['Patient_ID'], patient['Age'], patient['Gender']))
            
            # Insert studies
            unique_studies = df.drop_duplicates(subset=['Patient_ID', 'Modality', 'Folder_Path'])
            for _, study in unique_studies.iterrows():
                c.execute('''
                    INSERT OR IGNORE INTO patient_studies 
                    (patient_id, modality, folder_path, num_slices, study_date, ward_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (study['Patient_ID'], study['Modality'], study['Folder_Path'], 
                      study['Num_Slices'], study['Data of Study'], study['ward_id']))
            print("✅ Patient data loaded from master_metadata.csv")
    except FileNotFoundError:
        print("⚠️  master_metadata.csv not found - continuing without patient data")
    
    conn.commit()
    conn.close()
    print("✅ New database created with predefined medical staff")
    print("🎯 Medical Staff Credentials:")
    print("   - admin / admin123")
    print("   - dr_smith / smith123")
    print("   - tech_davis / davis123")
    print("   ... and others")

if __name__ == "__main__":
    reset_database()