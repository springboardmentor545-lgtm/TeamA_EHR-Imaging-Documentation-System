import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import streamlit as st

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('cardiac_clinic.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with predefined medical staff and patient structure"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if users table exists and has data
    try:
        c.execute('SELECT COUNT(*) FROM users')
        user_count = c.fetchone()[0]
        
        if user_count > 0:
            st.info("Database already initialized with data.")
            conn.close()
            return
    except sqlite3.OperationalError:
        # Table doesn't exist, continue with initialization
        pass
    
    # Drop existing tables
    c.execute('DROP TABLE IF EXISTS patient_studies')
    c.execute('DROP TABLE IF EXISTS patients')
    c.execute('DROP TABLE IF EXISTS reports')
    c.execute('DROP TABLE IF EXISTS users')
    
    # Create tables with correct schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
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
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS patient_studies (
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
        CREATE TABLE IF NOT EXISTS reports (
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
    
    # Insert predefined medical staff
    predefined_staff = [
        # Administrators
        ('admin', 'admin123', 'Administrator', 'System Administrator', 'admin@cardiacclinic.com', None),
        ('director', 'director123', 'Administrator', 'Hospital Director', 'director@cardiacclinic.com', None),
        
        # Doctors
        ('dr_smith', 'smith123', 'Doctor', 'Dr. John Smith', 'dr.smith@cardiacclinic.com', None),
        ('dr_jones', 'jones123', 'Doctor', 'Dr. Sarah Jones', 'dr.jones@cardiacclinic.com', None),
        ('dr_wilson', 'wilson123', 'Doctor', 'Dr. Michael Wilson', 'dr.wilson@cardiacclinic.com', None),
        
        # Technicians
        ('tech_davis', 'davis123', 'Technician', 'Robert Davis', 'tech.davis@cardiacclinic.com', None),
        ('tech_garcia', 'garcia123', 'Technician', 'Maria Garcia', 'tech.garcia@cardiacclinic.com', None),
        ('tech_lee', 'lee123', 'Technician', 'David Lee', 'tech.lee@cardiacclinic.com', None),
    ]
    
    for staff in predefined_staff:
        username, password, role, full_name, email, patient_id = staff
        c.execute('''
            INSERT OR IGNORE INTO users (username, password, role, full_name, email, patient_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, make_hashes(password), role, full_name, email, patient_id))
    
    # Load data from master_metadata.csv
    try:
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
    except FileNotFoundError:
        st.error("master_metadata.csv not found")
    
    conn.commit()
    conn.close()
    st.success("Database initialized with predefined medical staff!")

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def create_medical_staff(username, password, role, full_name, email):
    """Create new medical staff account (Admin/Doctor/Technician)"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role, full_name, email, patient_id) VALUES (?,?,?,?,?,?)',
                 (username, make_hashes(password), role, full_name, email, None))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_available_patient_ids():
    """Get list of patient IDs that don't have user accounts yet"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all patient IDs from patients table
    c.execute('SELECT patient_id FROM patients')
    all_patients = [row['patient_id'] for row in c.fetchall()]
    
    # Get patient IDs that already have user accounts
    c.execute('SELECT patient_id FROM users WHERE patient_id IS NOT NULL')
    registered_patients = [row['patient_id'] for row in c.fetchall()]
    
    # Find available patient IDs (not yet registered)
    available_patients = [pid for pid in all_patients if pid not in registered_patients]
    
    conn.close()
    return available_patients

def create_patient_user(patient_id, password, full_name, email):
    """Create patient user account linked to existing patient record"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if patient exists in patients table
    c.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    patient = c.fetchone()
    
    if not patient:
        return False, "Patient ID not found in system"
    
    # Check if patient already has a user account
    c.execute('SELECT * FROM users WHERE patient_id = ?', (patient_id,))
    existing_user = c.fetchone()
    
    if existing_user:
        return False, "Patient already has an account"
    
    try:
        # Create username from patient_id
        username = f"patient_{patient_id}"
        
        c.execute('INSERT INTO users (username, password, role, full_name, email, patient_id) VALUES (?,?,?,?,?,?)',
                 (username, make_hashes(password), 'Patient', full_name, email, patient_id))
        conn.commit()
        return True, "Patient account created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    
    if data and check_hashes(password, data['password']):
        return data
    return None

def get_all_patients():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM patients ORDER BY patient_id')
    patients = c.fetchall()
    conn.close()
    return patients

def get_patient_by_id(patient_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
    patient = c.fetchone()
    conn.close()
    return patient

def get_patient_studies(patient_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    if patient_id:
        c.execute('''
            SELECT ps.*, p.age, p.gender
            FROM patient_studies ps
            LEFT JOIN patients p ON ps.patient_id = p.patient_id
            WHERE ps.patient_id = ?
            ORDER BY ps.study_date DESC
        ''', (patient_id,))
    else:
        c.execute('''
            SELECT ps.*, p.age, p.gender
            FROM patient_studies ps
            LEFT JOIN patients p ON ps.patient_id = p.patient_id
            ORDER BY ps.study_date DESC
        ''')
    
    studies = c.fetchall()
    conn.close()
    return studies

def get_patient_by_user_id(user_id):
    """Get patient information for a user account"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.* 
        FROM patients p
        JOIN users u ON p.patient_id = u.patient_id
        WHERE u.id = ?
    ''', (user_id,))
    patient = c.fetchone()
    conn.close()
    return patient

def save_report_to_db(patient_id, modality, condition, icd10_code, image_features, findings, recommendations, clinical_report, formatted_report, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (patient_id, modality, condition_diagnosed, icd10_code, image_features, findings, recommendations, clinical_report, formatted_report, generated_by)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''', (patient_id, modality, condition, icd10_code, 
          image_features, findings, recommendations, clinical_report, formatted_report, user_id))
    conn.commit()
    conn.close()

def get_patient_reports(patient_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.*, u.full_name as generated_by_name 
        FROM reports r 
        LEFT JOIN users u ON r.generated_by = u.id 
        WHERE r.patient_id = ? 
        ORDER BY r.created_at DESC
    ''', (patient_id,))
    reports = c.fetchall()
    conn.close()
    return reports

def get_all_reports():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.*, u.full_name as generated_by_name, p.age, p.gender
        FROM reports r 
        LEFT JOIN users u ON r.generated_by = u.id 
        LEFT JOIN patients p ON r.patient_id = p.patient_id
        ORDER BY r.created_at DESC
    ''')
    reports = c.fetchall()
    conn.close()
    return reports

def get_dashboard_stats():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(DISTINCT patient_id) FROM patients')
    total_patients = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM reports')
    total_reports = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM patient_studies')
    total_studies = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM reports WHERE DATE(created_at) >= DATE("now", "-7 days")')
    recent_reports = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_patients': total_patients,
        'total_reports': total_reports,
        'total_studies': total_studies,
        'recent_reports': recent_reports
    }

def delete_report(report_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM reports WHERE id = ?', (report_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting report: {e}")
        return False
    finally:
        conn.close()

def delete_all_patient_reports(patient_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM reports WHERE patient_id = ?', (patient_id,))
        conn.commit()
        return c.rowcount
    except Exception as e:
        st.error(f"Error deleting patient reports: {e}")
        return 0
    finally:
        conn.close()

def cleanup_duplicates():
    """Clean up duplicate entries in database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        DELETE FROM patient_studies 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM patient_studies 
            GROUP BY patient_id, modality, folder_path
        )
    ''')
    
    c.execute('''
        DELETE FROM patients 
        WHERE rowid NOT IN (
            SELECT MIN(rowid) 
            FROM patients 
            GROUP BY patient_id
        )
    ''')
    
    conn.commit()
    conn.close()
    st.success("Duplicate entries cleaned up!")
# Add these functions to your database.py

def get_all_users():
    """Get all users (Admin only)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, username, role, full_name, email, patient_id, created_at 
        FROM users 
        ORDER BY role, username
    ''')
    users = c.fetchall()
    conn.close()
    return users

def get_medical_staff():
    """Get all medical staff (non-patient users)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, username, role, full_name, email, created_at 
        FROM users 
        WHERE role != 'Patient' 
        ORDER BY role, username
    ''')
    staff = c.fetchall()
    conn.close()
    return staff

def delete_user(user_id):
    """Delete a user (Admin only)"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Don't allow deleting the main admin account
        c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        
        if user and user['username'] == 'admin':
            return False, "Cannot delete the main administrator account"
        
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return True, "User deleted successfully"
    except sqlite3.Error as e:
        return False, f"Error deleting user: {str(e)}"
    finally:
        conn.close()

def update_user_role(user_id, new_role):
    """Update user role (Admin only)"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Don't allow changing admin role
        c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        
        if user and user['username'] == 'admin' and new_role != 'Administrator':
            return False, "Cannot change role of main administrator account"
        
        c.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
        conn.commit()
        return True, "User role updated successfully"
    except sqlite3.Error as e:
        return False, f"Error updating user role: {str(e)}"
    finally:
        conn.close()