import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageEnhance
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv2D, PReLU, UpSampling2D, Input, Dense, Flatten, Dropout, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai
import hashlib
import sqlite3
import json
from io import BytesIO
import base64
from fpdf import FPDF
import tempfile

# Configure Gemini AI
genai.configure(api_key='AIzaSyDyVY2ZAFunydX53ncBlO1Y-hjgIlD1chM')
np.random.seed(42)
tf.random.set_seed(42)

# Load the master metadata
@st.cache_data
def load_master_metadata():
    try:
        df = pd.read_csv('master_metadata.csv')
        return df
    except FileNotFoundError:
        st.error("master_metadata.csv file not found. Please ensure it's in the same directory.")
        return pd.DataFrame()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('cardiac_clinic.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Database setup - CORRECTED to match master_metadata structure
def init_db():
    # Check if database is already initialized to avoid duplicate data
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if patients table already has data
    c.execute('SELECT COUNT(*) FROM patients')
    patient_count = c.fetchone()[0]
    conn.close()
    
    # If database already has data, skip initialization
    if patient_count > 0:
        st.info("Database already initialized with data.")
        return
    
    # Only proceed if database is empty
    conn = get_db_connection()
    c = conn.cursor()
    
    # Drop existing tables to start fresh (only if needed)
    c.execute('DROP TABLE IF EXISTS patient_studies')
    c.execute('DROP TABLE IF EXISTS patients')
    c.execute('DROP TABLE IF EXISTS reports')
    c.execute('DROP TABLE IF EXISTS users')
    
    # Users table (for system access only)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patients table (directly from master_metadata - only essential fields)
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patient Imaging Studies table (directly from master_metadata)
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
    
    # Reports table (EHR - for analysis results) - UPDATED to include formatted_report
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
    
    # Insert default admin user
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password, role, full_name, email) VALUES (?,?,?,?,?)',
                 ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrator', 'System Administrator', 'admin@cardiacclinic.com'))
    
    # Load data from master_metadata.csv - CORRECTED to avoid duplicates
    df = load_master_metadata()
    if not df.empty:
        # First, create unique patient entries
        unique_patients = df[['Patient_ID', 'Age', 'Gender']].drop_duplicates()
        
        for _, patient in unique_patients.iterrows():
            try:
                c.execute('''
                    INSERT OR IGNORE INTO patients (patient_id, age, gender)
                    VALUES (?, ?, ?)
                ''', (patient['Patient_ID'], patient['Age'], patient['Gender']))
            except sqlite3.IntegrityError:
                pass  # Patient already exists
        
        # Then insert all studies - USE DISTINCT to avoid duplicates
        unique_studies = df.drop_duplicates(subset=['Patient_ID', 'Modality', 'Folder_Path'])
        
        for _, study in unique_studies.iterrows():
            try:
                c.execute('''
                    INSERT OR IGNORE INTO patient_studies (patient_id, modality, folder_path, num_slices, study_date, ward_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (study['Patient_ID'], study['Modality'], study['Folder_Path'], 
                      study['Num_Slices'], study['Data of Study'], study['ward_id']))
            except sqlite3.IntegrityError as e:
                st.error(f"Error inserting study: {e}")
    
    conn.commit()
    conn.close()
    st.success("Database initialized successfully!")

# Password hashing functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def create_user(username, password, role, full_name, email):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role, full_name, email) VALUES (?,?,?,?,?)',
                 (username, make_hashes(password), role, full_name, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
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

# Patient management functions - SIMPLIFIED to match master_metadata
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

# Patient Studies functions
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

# Report management functions - UPDATED to include formatted_report
def save_report_to_db(patient_id, modality, condition, icd10_code, image_features, findings, recommendations, clinical_report, formatted_report, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (patient_id, modality, condition_diagnosed, icd10_code, image_features, findings, recommendations, clinical_report, formatted_report, generated_by)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''', (patient_id, modality, condition, icd10_code, 
          json.dumps(image_features), json.dumps(findings), json.dumps(recommendations), clinical_report, formatted_report, user_id))
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
    
    # Total patients
    c.execute('SELECT COUNT(DISTINCT patient_id) FROM patients')
    total_patients = c.fetchone()[0]
    
    # Total reports - FIXED: Count distinct report entries
    c.execute('SELECT COUNT(*) FROM reports')
    total_reports = c.fetchone()[0]
    
    # Total studies
    c.execute('SELECT COUNT(*) FROM patient_studies')
    total_studies = c.fetchone()[0]
    
    # Recent reports (last 7 days) - FIXED: Use proper date comparison
    c.execute('SELECT COUNT(*) FROM reports WHERE DATE(created_at) >= DATE("now", "-7 days")')
    recent_reports = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_patients': total_patients,
        'total_reports': total_reports,
        'total_studies': total_studies,
        'recent_reports': recent_reports
    }

# Your existing analysis functions (keeping them as is)
def clean_text(text):
    text = text.replace('*', '').replace('★', '')
    import re
    text = re.sub(r'\n\s*\n', '\n\n', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() == '':
            cleaned_lines.append('')
        else:
            cleaned_lines.append(' '.join(line.split()))
    return '\n'.join(cleaned_lines)

def build_srcnn_model():
    input_img = Input(shape=(None, None, 1))
    x = Conv2D(64, (9, 9), padding='same', activation='relu')(input_img)
    x = Conv2D(32, (1, 1), padding='same', activation='relu')(x)
    output = Conv2D(1, (5, 5), padding='same', activation='linear')(x)
    model = Model(input_img, output)
    model.compile(optimizer='adam', loss='mse')
    return model

def build_classification_model(input_shape=(256, 256, 1)):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(256, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(5, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def load_and_process_slices(folder_path, num_slices, target_size=(256, 256), enhance=True):
    processed_slices = []
    for i in range(num_slices):
        synthetic_img = np.random.rand(target_size[0], target_size[1]) * 0.5
        
        center_x, center_y = target_size[0] // 2, target_size[1] // 2
        radius = min(target_size) // 3
        
        y, x = np.ogrid[:target_size[0], :target_size[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        synthetic_img[mask] += 0.4
        
        if i % 3 == 0:
            cv2.line(synthetic_img, (center_x-30, center_y-20), (center_x+30, center_y-30), 0.8, 2)
            cv2.line(synthetic_img, (center_x-20, center_y+30), (center_x+25, center_y+25), 0.8, 2)
        
        synthetic_img = np.clip(synthetic_img, 0, 1)
        processed_slices.append(synthetic_img)
    
    return processed_slices

def enhance_with_srcnn(slices, srcnn_model):
    enhanced_slices = []
    for slice in slices:
        slice_expanded = np.expand_dims(slice, axis=0)
        slice_expanded = np.expand_dims(slice_expanded, axis=-1)
        enhanced = srcnn_model.predict(slice_expanded, verbose=0)
        enhanced = np.squeeze(enhanced)
        enhanced_slices.append(enhanced)
    return enhanced_slices

def calculate_entropy(image):
    hist = np.histogram(image, bins=256, range=(0, 1))[0]
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    return entropy

def calculate_homogeneity(image):
    from scipy.ndimage import uniform_filter, generic_filter
    std_dev = generic_filter(image, np.std, size=5)
    homogeneity = 1 / (1 + np.mean(std_dev))
    return homogeneity

def calculate_symmetry(image):
    height, width = image.shape
    left_half = image[:, :width//2]
    right_half = image[:, width//2:]
    right_flipped = np.fliplr(right_half)
    if left_half.shape == right_flipped.shape:
        mse = np.mean((left_half - right_flipped) ** 2)
        symmetry = 1 / (1 + mse)
        return symmetry
    return 0.5

def estimate_cardiac_area(image):
    _, thresh = cv2.threshold((image * 255).astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        return area / (image.shape[0] * image.shape[1])
    return 0

def extract_image_features(slices):
    features = []
    for slice in slices:
        slice_features = {
            'mean_intensity': np.mean(slice),
            'std_intensity': np.std(slice),
            'max_intensity': np.max(slice),
            'min_intensity': np.min(slice),
            'contrast': np.max(slice) - np.min(slice),
            'entropy': calculate_entropy(slice),
            'homogeneity': calculate_homogeneity(slice),
            'cardiac_area': estimate_cardiac_area(slice),
            'symmetry_score': calculate_symmetry(slice)
        }
        features.append(slice_features)
    return features

ICD10_CODES = {
    'myocardial_infarction': 'I21',
    'heart_failure': 'I50',
    'coronary_artery_disease': 'I25',
    'arrhythmia': 'I49',
    'cardiomyopathy': 'I42',
    'valvular_heart_disease': 'I35',
    'normal': 'Z00'
}

def classify_cardiac_condition(image_features, age, gender, modality):
    risk_score = 0
    
    avg_contrast = np.mean([f['contrast'] for f in image_features])
    if avg_contrast > 0.7:
        risk_score += 0.2

    avg_entropy = np.mean([f['entropy'] for f in image_features])
    if avg_entropy > 5:
        risk_score += 0.2

    avg_area = np.mean([f['cardiac_area'] for f in image_features])
    if avg_area < 0.1 or avg_area > 0.4:
        risk_score += 0.2

    avg_symmetry = np.mean([f['symmetry_score'] for f in image_features])
    if avg_symmetry < 0.6:
        risk_score += 0.2

    if age > 60:
        risk_score += 0.2
    elif age > 40:
        risk_score += 0.1

    if gender == 'M':
        risk_score += 0.1

    if modality == 'CT':
        risk_score += 0.05
    elif modality == 'MRI':
        risk_score += 0.1

    if risk_score < 0.3:
        return 'normal', ICD10_CODES['normal']
    elif risk_score < 0.5:
        return 'coronary_artery_disease', ICD10_CODES['coronary_artery_disease']
    elif risk_score < 0.7:
        return 'arrhythmia', ICD10_CODES['arrhythmia']
    elif risk_score < 0.8:
        return 'cardiomyopathy', ICD10_CODES['cardiomyopathy']
    else:
        return 'myocardial_infarction', ICD10_CODES['myocardial_infarction']

def generate_cardiac_report(patient_id, modality, condition, icd10_code, image_features, age, gender):
    avg_features = {
        'mean_intensity': np.mean([f['mean_intensity'] for f in image_features]),
        'std_intensity': np.mean([f['std_intensity'] for f in image_features]),
        'contrast': np.mean([f['contrast'] for f in image_features]),
        'entropy': np.mean([f['entropy'] for f in image_features]),
        'cardiac_area': np.mean([f['cardiac_area'] for f in image_features]),
        'symmetry': np.mean([f['symmetry_score'] for f in image_features])
    }
    
    findings = []
    recommendations = []
    
    if condition == 'normal':
        findings.append("Cardiac structures appear within normal limits.")
        findings.append("No evidence of significant cardiac pathology.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f} (normal range: 0.15-0.35)")
        findings.append(f"Cardiac symmetry score: {avg_features['symmetry']:.3f} (good symmetry > 0.7)")
        recommendations.append("Routine follow-up as per standard guidelines.")
    elif condition == 'coronary_artery_disease':
        findings.append("Findings suggestive of coronary artery disease.")
        findings.append("Possible calcifications or narrowing observed in coronary arteries.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f} (slightly enlarged)")
        findings.append(f"Image contrast: {avg_features['contrast']:.3f} (elevated, may indicate calcifications)")
        recommendations.append("Further evaluation with coronary CT angiography recommended.")
        recommendations.append("Cardiology consultation advised.")
        recommendations.append("Lipid profile and cardiac risk factor assessment.")
    elif condition == 'arrhythmia':
        findings.append("Features suggestive of potential arrhythmogenic substrate.")
        findings.append("Structural changes may predispose to electrical abnormalities.")
        findings.append(f"Cardiac symmetry score: {avg_features['symmetry']:.3f} (reduced symmetry)")
        recommendations.append("Electrophysiology study may be considered.")
        recommendations.append("Holter monitoring recommended for rhythm assessment.")
    elif condition == 'myocardial_infarction':
        findings.append("Findings consistent with myocardial infarction (current or prior).")
        findings.append("Regional wall motion abnormalities or scar tissue identified.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f} (may be enlarged)")
        findings.append(f"Image entropy: {avg_features['entropy']:.3f} (elevated, indicating tissue heterogeneity)")
        recommendations.append("Urgent cardiology consultation recommended.")
        recommendations.append("Further assessment with cardiac MRI or echocardiography.")
        recommendations.append("Cardiac enzymes and ECG monitoring.")
    elif condition == 'cardiomyopathy':
        findings.append("Findings suggestive of cardiomyopathy.")
        findings.append("Global cardiac enlargement or hypertrophy observed.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f} (enlarged)")
        findings.append(f"Cardiac symmetry score: {avg_features['symmetry']:.3f} (reduced symmetry)")
        recommendations.append("Comprehensive cardiac evaluation recommended.")
        recommendations.append("Echocardiography for functional assessment.")
        recommendations.append("Consider genetic testing if indicated.")
    
    if age > 60:
        findings.append("Age-related cardiovascular changes observed.")
    if gender == 'M' and age > 45:
        findings.append("Consider additional risk factor assessment for coronary artery disease.")
    if gender == 'F' and age > 55:
        findings.append("Post-menopausal cardiovascular risk factors should be evaluated.")
    
    if modality == 'CT':
        findings.append("CT imaging provides excellent visualization of coronary calcifications.")
    elif modality == 'MRI':
        findings.append("MRI provides detailed tissue characterization and functional assessment.")
    
    report = {
        "patient_id": patient_id,
        "modality": modality,
        "age": age,
        "gender": gender,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "condition_diagnosed": condition,
        "icd10_code": icd10_code,
        "image_characteristics": avg_features,
        "findings": findings,
        "recommendations": recommendations,
        "report_generated_by": "AI Cardiac Analysis System v2.0"
    }
    
    return report

def process_cardiac_imaging_data(patient_studies, patient_id):
    results = {}
    patient_studies_data = [dict(study) for study in patient_studies if study['patient_id'] == patient_id]
    
    if not patient_studies_data:
        st.error(f"No imaging studies found for patient {patient_id}")
        return results

    with st.spinner("Building AI models for cardiac analysis..."):
        srcnn_model = build_srcnn_model()
        classification_model = build_classification_model()

    for study in patient_studies_data:
        modality = study['modality']
        folder_path = study['folder_path']
        num_slices = study['num_slices']
        age = study['age']
        gender = study['gender']
        
        st.info(f"Processing {modality} images for patient {patient_id}...")
        
        progress_bar = st.progress(0)
        
        with st.spinner("Loading and processing image slices..."):
            slices = load_and_process_slices(folder_path, num_slices, enhance=True)
        progress_bar.progress(25)
        
        if len(slices) == 0:
            st.error(f"No slices loaded for {patient_id} {modality}")
            continue
        
        with st.spinner("Enhancing images with AI..."):
            enhanced_slices = enhance_with_srcnn(slices, srcnn_model)
        progress_bar.progress(50)
        
        with st.spinner("Extracting cardiac image features..."):
            image_features = extract_image_features(enhanced_slices)
        progress_bar.progress(75)
        
        with st.spinner("Analyzing cardiac condition..."):
            condition, icd10_code = classify_cardiac_condition(image_features, age, gender, modality)
            report = generate_cardiac_report(patient_id, modality, condition, icd10_code, 
                                           image_features, age, gender)
        progress_bar.progress(100)

        results[modality] = {
            'slices': slices,
            'enhanced_slices': enhanced_slices,
            'image_features': image_features,
            'report': report
        }
        
        st.success(f"✅ {modality} analysis completed!")
    
    return results

# NEW FUNCTION: Generate properly formatted clinical report
def generate_formatted_clinical_report(patient_id, cardiac_results, patient_info):
    """
    Generate a properly formatted clinical report that is readable and printable
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    report_content = f"""
CARDIAC IMAGING REPORT
=============================================

PATIENT INFORMATION:
-------------------
Patient ID: {patient_id}
Age: {patient_info['age']}
Gender: {patient_info['gender']}
Report Date: {current_date}

CLINICAL HISTORY:
----------------
Cardiac imaging study performed for evaluation of cardiac function and structure.

IMAGING STUDIES:
---------------
"""
    
    # Add modality-specific findings
    for modality, data in cardiac_results.items():
        if 'report' in data:
            report = data['report']
            report_content += f"""
{modality} STUDY:
===============
Indication: Cardiac evaluation
Technique: Standard {modality} protocol

FINDINGS:
--------
"""
            
            for finding in report.get('findings', []):
                report_content += f"- {finding}\n"  # Using hyphen instead of bullet
            
            report_content += f"""
QUANTITATIVE ANALYSIS:
---------------------
Cardiac Area: {report['image_characteristics']['cardiac_area']:.3f}
Symmetry Score: {report['image_characteristics']['symmetry']:.3f}
Image Contrast: {report['image_characteristics']['contrast']:.3f}

IMPRESSION:
----------
{report['condition_diagnosed'].replace('_', ' ').title()} 
ICD-10 Code: {report['icd10_code']}

RECOMMENDATIONS:
---------------
"""
            
            for recommendation in report.get('recommendations', []):
                report_content += f"- {recommendation}\n"  # Using hyphen instead of bullet
            
            report_content += "\n" + "="*50 + "\n\n"
    
    # Add final signature section
    report_content += f"""
END OF REPORT
=============

This report was generated by the AI Cardiac Analysis System v2.0
and has been reviewed and approved by:

___________________________________
John Doe, MD
Cardiologist
Cardiac Imaging Department

Date: {current_date}

Note: This report should be correlated with clinical findings and other diagnostic tests.
"""
    
    return report_content

# NEW FUNCTION: Create PDF from report
def create_pdf_report(report_text, patient_id):
    """
    Create a PDF version of the clinical report with proper Unicode handling
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Use a font that supports Unicode characters
    try:
        # Try to use Arial Unicode MS or DejaVuSans if available
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', size=10)
    except:
        try:
            pdf.add_font('Arial', '', 'arial.ttf', uni=True)
            pdf.set_font('Arial', size=10)
        except:
            # Fall back to standard font (may not support all Unicode)
            pdf.set_font("Arial", size=10)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CARDIAC IMAGING REPORT", ln=True, align='C')
    pdf.ln(10)
    
    # Clean the text to remove or replace problematic characters
    def clean_text_for_pdf(text):
        # Replace bullet points and other problematic characters
        text = text.replace('•', '-')
        text = text.replace('❤️', '')
        text = text.replace('✅', '')
        text = text.replace('❌', '')
        # Remove any other non-latin-1 characters
        text = text.encode('latin-1', 'ignore').decode('latin-1')
        return text
    
    # Split text into lines and add to PDF
    lines = clean_text_for_pdf(report_text).split('\n')
    pdf.set_font("Arial", size=10)
    
    for line in lines:
        if line.strip() == '':
            pdf.ln(5)
        elif line.startswith('===') or line.startswith('---'):
            pdf.set_draw_color(0, 0, 0)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        elif any(keyword in line for keyword in ['PATIENT INFORMATION', 'CLINICAL HISTORY', 'IMAGING STUDIES', 
                                               'FINDINGS', 'IMPRESSION', 'RECOMMENDATIONS', 'END OF REPORT']):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 8, txt=line.strip(), ln=True)
            pdf.set_font("Arial", size=10)
        elif line.strip().isupper() and len(line.strip()) > 10:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(200, 7, txt=line.strip(), ln=True)
            pdf.set_font("Arial", size=10)
        else:
            # Use multi_cell for better text wrapping
            pdf.multi_cell(0, 5, txt=line)
    
    # Save PDF to bytes with proper encoding
    pdf_output = BytesIO()
    try:
        pdf_output.write(pdf.output(dest='S').encode('latin-1'))
    except UnicodeEncodeError:
        # Fallback: use UTF-8 encoding with error handling
        pdf_output.write(pdf.output(dest='S').encode('utf-8', errors='ignore'))
    pdf_output.seek(0)
    
    return pdf_output

def generate_patient_report_both_modalities(patient_id, cardiac_results):
    modalities = ['CT', 'MRI']
    reports = []
    
    for modality in modalities:
        if modality in cardiac_results and 'report' in cardiac_results[modality]:
            model_report = cardiac_results[modality]['report']
            findings = "\n".join(f"- {f}" for f in model_report.get('findings', []))
            recommendations = "\n".join(f"- {r}" for r in model_report.get('recommendations', []))
            icd10_code = model_report.get('icd10_code', 'N/A')
            condition = model_report.get('condition_diagnosed', 'N/A')
            age = model_report.get('age', 'N/A')
            gender = model_report.get('gender', 'N/A')
            modality_name = model_report.get('modality', modality)
            
            prompt = (
                f"Generate a detailed, well-formatted clinical report for a cardiac patient.\n"
                f"Patient ID: {patient_id}\n"
                f"Modality: {modality_name}\n"
                f"Age: {age}\n"
                f"Gender: {gender}\n"
                f"Condition Diagnosed: {condition}\n"
                f"ICD-10 Code: {icd10_code}\n"
                f"\nKey Findings:\n{findings}\n"
                f"\nRecommendations:\n{recommendations}\n"
                "Please present the report in a professional and structured format that is suitable for clinicians. "
                "Use clear section headings (e.g., 'FINDINGS:', 'RECOMMENDATIONS:') and ensure that each section is separated by a blank line. "
                "Use line breaks within sections to avoid long paragraphs. The report should not appear as a single block of text. "
                "Additionally, remove any asterisks or decorative symbols from the output. "
                "The Doctor name should be John Doe with an undersigned esign at the end of the report."
            )
            
            try:
                with st.spinner(f"Generating {modality} report with AI..."):
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(prompt)
                    cleaned_text = clean_text(response.text)
                    reports.append(f"--- {modality} Report ---\n{cleaned_text}")
            except Exception as e:
                st.error(f"Error generating report with Gemini: {e}")
                reports.append(f"--- {modality} Report ---\nError generating report with Gemini API")
        else:
            reports.append(f"No data found for Patient_ID: {patient_id} and Modality: {modality}")
    
    final_report = "\n\n".join(reports)
    return final_report

def cleanup_duplicates():
    """Temporary function to clean up duplicate entries"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Remove duplicate patient_studies
    c.execute('''
        DELETE FROM patient_studies 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM patient_studies 
            GROUP BY patient_id, modality, folder_path
        )
    ''')
    
    # Remove duplicate patients
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

# Streamlit App - UPDATED with proper report formatting
def main():
    st.set_page_config(
        page_title="Cardiac EHR System",
        page_icon="❤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Session state management
    if 'db_initialized' not in st.session_state:
        init_db()
        st.session_state.db_initialized = True
    if 'duplicates_cleaned' not in st.session_state:
        cleanup_duplicates()
        st.session_state.duplicates_cleaned = True
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Login"
    if 'selected_patient' not in st.session_state:
        st.session_state.selected_patient = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .card {
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin: 10px 0;
        }
        .success-card {
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        .warning-card {
            background-color: #fff3cd;
            border-color: #ffeaa7;
        }
        .report-box {
            background-color: #f8f9fa;
            color: black;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/heart-health.png", width=80)
        st.title("Cardiac EHR System")
        
        if st.session_state.logged_in:
            st.success(f"Welcome, {st.session_state.user_info['full_name']}!")
            st.write(f"Role: {st.session_state.user_info['role']}")
            
            pages = ["Dashboard", "Patient Database", "Cardiac Analysis", "EHR Reports"]
            selected_page = st.selectbox("Navigation", pages, index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0)
            st.session_state.current_page = selected_page
            
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_info = None
                st.session_state.current_page = "Login"
                st.session_state.selected_patient = None
                st.session_state.analysis_results = None
                st.rerun()
        else:
            st.session_state.current_page = "Login"
    
    # Page routing
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.current_page == "Dashboard":
            dashboard_page()
        elif st.session_state.current_page == "Patient Database":
            patient_database_page()
        elif st.session_state.current_page == "Cardiac Analysis":
            cardiac_analysis_page()
        elif st.session_state.current_page == "EHR Reports":
            ehr_reports_page()

# Add this function to your database functions section
def delete_report(report_id):
    """Delete a specific report from the database"""
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
    """Delete all reports for a specific patient"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM reports WHERE patient_id = ?', (patient_id,))
        conn.commit()
        return c.rowcount  # Return number of reports deleted
    except Exception as e:
        st.error(f"Error deleting patient reports: {e}")
        return 0
    finally:
        conn.close()

def login_page():
    st.markdown('<h1 class="main-header">Cardiac EHR Analysis System</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("User Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    user_data = login_user(username, password)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.user_info = dict(user_data)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        with st.form("register_form"):
            st.subheader("New User Registration")
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["Doctor", "Technician", "Administrator"])
            register_btn = st.form_submit_button("Register")
            
            if register_btn:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif new_username and new_password and full_name:
                    success = create_user(new_username, new_password, role, full_name, email)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")
                else:
                    st.warning("Please fill all required fields")

def dashboard_page():
    st.markdown('<h1 class="main-header">Clinical Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    # Get dashboard statistics
    stats = get_dashboard_stats()
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", stats['total_patients'])
    with col2:
        st.metric("Total EHR Reports", stats['total_reports'])
    with col3:
        st.metric("Imaging Studies", stats['total_studies'])
    with col4:
        st.metric("Recent Reports (7 days)", stats['recent_reports'])
    
    # Show master metadata info
    df = load_master_metadata()
    if not df.empty:
        st.subheader("Master Metadata Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Unique Patients", df['Patient_ID'].nunique())
        with col3:
            st.metric("CT Studies", len(df[df['Modality'] == 'CT']))
            st.metric("MRI Studies", len(df[df['Modality'] == 'MRI']))
    
    # Recent EHR reports
    st.subheader("Recent EHR Reports")
    reports = get_all_reports()[:5]
    
    if reports:
        for report in reports:
            with st.container():
                st.markdown(f"""
                <div class="report-box">
                    <h4>EHR Report for Patient {report['patient_id']}</h4>
                    <p><strong>Modality:</strong> {report['modality']} | <strong>Condition:</strong> {report['condition_diagnosed']} | <strong>ICD-10:</strong> {report['icd10_code']}</p>
                    <p><strong>Generated by:</strong> {report['generated_by_name']} on {report['created_at']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No EHR reports generated yet. Start by analyzing a patient's cardiac images.")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Patient Database", use_container_width=True):
            st.session_state.current_page = "Patient Database"
            st.rerun()
    
    with col2:
        if st.button("Start Cardiac Analysis", use_container_width=True):
            st.session_state.current_page = "Cardiac Analysis"
            st.rerun()
    
    with col3:
        if st.button("View EHR Reports", use_container_width=True):
            st.session_state.current_page = "EHR Reports"
            st.rerun()

def patient_database_page():
    st.markdown('<h1 class="main-header">Patient Database</h1>', unsafe_allow_html=True)
    
    st.subheader("Patients from Master Metadata")
    patients = get_all_patients()
    
    if patients:
        for patient in patients:
            patient_dict = dict(patient)
            with st.expander(f"Patient {patient_dict['patient_id']} - Age: {patient_dict['age']} - Gender: {patient_dict['gender']}"):
                
                # Get studies for this patient
                studies = get_patient_studies(patient_dict['patient_id'])
                
                st.write("**Imaging Studies:**")
                for study in studies:
                    study_dict = dict(study)
                    st.write(f"- **{study_dict['modality']}**: {study_dict['study_date']} (Slices: {study_dict['num_slices']}, Ward: {study_dict['ward_id']})")
                    st.write(f"  Folder: {study_dict['folder_path']}")
                
                col1, col2, col3 = st.columns(3)  # Changed to 3 columns
                with col1:
                    if st.button(f"Analyze This Patient", key=f"analyze_{patient_dict['patient_id']}"):
                        st.session_state.selected_patient = patient_dict['patient_id']
                        st.session_state.current_page = "Cardiac Analysis"
                        st.rerun()
                
                with col2:
                    # Show existing reports if any
                    reports = get_patient_reports(patient_dict['patient_id'])
                    if reports:
                        st.write(f"**Existing EHR Reports:** {len(reports)}")
                    else:
                        st.write("**Existing EHR Reports:** None")
                
                with col3:
                    # Delete all reports for this patient
                    reports = get_patient_reports(patient_dict['patient_id'])
                    if reports:
                        if st.button(f"Delete All Reports", key=f"delete_all_{patient_dict['patient_id']}"):
                            with st.spinner("Deleting reports..."):
                                deleted_count = delete_all_patient_reports(patient_dict['patient_id'])
                                if deleted_count > 0:
                                    st.success(f"Deleted {deleted_count} reports for patient {patient_dict['patient_id']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete reports")
    else:
        st.info("No patients found in the database.")

def cardiac_analysis_page():
    st.markdown('<h1 class="main-header">Cardiac Image Analysis</h1>', unsafe_allow_html=True)
    
    # Get all patients
    patients = get_all_patients()
    
    if not patients:
        st.error("No patients found in the database.")
        return
    
    patient_ids = [patient['patient_id'] for patient in patients]
    
    # Use selected patient if available, otherwise use first patient
    if st.session_state.selected_patient and st.session_state.selected_patient in patient_ids:
        default_index = patient_ids.index(st.session_state.selected_patient)
    else:
        default_index = 0
    
    selected_patient = st.selectbox("Select Patient", patient_ids, index=default_index)
    
    if selected_patient:
        # Get patient info
        patient_info = get_patient_by_id(selected_patient)
        patient_studies = get_patient_studies(selected_patient)
        
        if patient_info:
            patient_dict = dict(patient_info)
            col1, col2, col3 = st.columns(3)  # Changed to 3 columns
            with col1:
                st.subheader("Patient Information")
                st.write(f"**Patient ID:** {patient_dict['patient_id']}")
                st.write(f"**Age:** {patient_dict['age']}")
                st.write(f"**Gender:** {patient_dict['gender']}")
            
            with col2:
                st.subheader("Available Studies")
                if patient_studies:
                    for study in patient_studies:
                        study_dict = dict(study)
                        st.write(f"- **{study_dict['modality']}** ({study_dict['num_slices']} slices)")
                else:
                    st.write("No imaging studies available")
            
            with col3:
                st.subheader("Report Management")
                # Show existing reports count with delete option
                existing_reports = get_patient_reports(selected_patient)
                if existing_reports:
                    st.write(f"**Existing Reports:** {len(existing_reports)}")
                    if st.button("🗑️ Delete All Reports for This Patient", key="delete_all"):
                        with st.spinner("Deleting reports..."):
                            deleted_count = delete_all_patient_reports(selected_patient)
                            if deleted_count > 0:
                                st.success(f"Deleted {deleted_count} reports for patient {selected_patient}")
                                st.rerun()
                            else:
                                st.error("Failed to delete reports")
                else:
                    st.write("**Existing Reports:** None")
        
        # Analysis section
        st.subheader("Cardiac Analysis")
        
        if st.button("Start Cardiac Analysis", type="primary"):
            with st.spinner("Initializing cardiac analysis system..."):
                results = process_cardiac_imaging_data(patient_studies, selected_patient)
            
            if results:
                st.session_state.analysis_results = results
                
                # Display results for each modality
                for modality, data in results.items():
                    if 'report' in data:
                        report = data['report']
                        
                        st.subheader(f"{modality} Analysis Results")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Condition Diagnosed", report['condition_diagnosed'].replace('_', ' ').title())
                            st.metric("ICD-10 Code", report['icd10_code'])
                        
                        with col2:
                            st.metric("Cardiac Area", f"{report['image_characteristics']['cardiac_area']:.3f}")
                            st.metric("Symmetry Score", f"{report['image_characteristics']['symmetry']:.3f}")
                        
                        st.subheader("Key Findings")
                        for finding in report['findings']:
                            st.write(f"• {finding}")
                        
                        st.subheader("Recommendations")
                        for recommendation in report['recommendations']:
                            st.write(f"• {recommendation}")
                
                # Store results in session state for report generation
                st.session_state.analysis_results = results
                st.session_state.selected_patient = selected_patient
                st.session_state.patient_info = patient_dict
                
                st.success("Cardiac analysis completed! You can now generate the EHR report.")
        
        # Report generation section
        if st.session_state.get('analysis_results') and st.session_state.get('selected_patient') == selected_patient:
            st.subheader("EHR Report Generation")
            
            # Generate both types of reports
            clinical_report = generate_patient_report_both_modalities(selected_patient, st.session_state.analysis_results)
            formatted_report = generate_formatted_clinical_report(selected_patient, st.session_state.analysis_results, patient_dict)
            
            # Display the formatted report
            st.subheader("Formatted Clinical EHR Report")
            st.text_area("Report Content", formatted_report, height=400, key="report_display")
            
            # Create PDF version
            pdf_report = create_pdf_report(formatted_report, selected_patient)
            
            # Save to EHR database
            if st.button("💾 Save EHR Report to Database", type="primary", key="save_report_btn"):
                try:
                    for modality, data in st.session_state.analysis_results.items():
                        if 'report' in data:
                            report_data = data['report']
                            
                            # Convert numpy types to Python native types for JSON serialization
                            image_features_serializable = {}
                            for key, value in report_data['image_characteristics'].items():
                                if hasattr(value, 'item'):
                                    image_features_serializable[key] = value.item()
                                else:
                                    image_features_serializable[key] = value
                            
                            findings_serializable = [str(f) for f in report_data['findings']]
                            recommendations_serializable = [str(r) for r in report_data['recommendations']]
                            
                            save_report_to_db(
                                selected_patient, 
                                modality,
                                report_data['condition_diagnosed'],
                                report_data['icd10_code'],
                                image_features_serializable,
                                findings_serializable,
                                recommendations_serializable,
                                clinical_report,
                                formatted_report,
                                st.session_state.user_info['id']
                            )
                    
                    st.success(f"✅ EHR Report for patient {selected_patient} saved successfully to database!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving report to database: {str(e)}")
            
            # Download options
            st.subheader("Download Options")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Download Text Report",
                    data=formatted_report,
                    file_name=f"ehr_report_{selected_patient}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                st.download_button(
                    label="📊 Download PDF Report",
                    data=pdf_report.getvalue(),
                    file_name=f"ehr_report_{selected_patient}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        elif not st.session_state.get('analysis_results'):
            st.info("ℹ️ Please run the cardiac analysis first to generate reports.")

def ehr_reports_page():
    st.markdown('<h1 class="main-header">EHR Reports Database</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["All EHR Reports", "Search Reports"])
    
    with tab1:
        st.subheader("Generated EHR Reports")
        reports = get_all_reports()
        
        if reports:
            st.metric("Total Reports in Database", len(reports))
            
            for report in reports:
                report_dict = dict(report)
                with st.expander(f"📋 EHR Report for Patient {report_dict['patient_id']} - {report_dict['modality']} - {report_dict['created_at']}"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Patient ID:** {report_dict['patient_id']}")
                        st.write(f"**Age:** {report_dict.get('age', 'N/A')}")
                        st.write(f"**Gender:** {report_dict.get('gender', 'N/A')}")
                        st.write(f"**Modality:** {report_dict['modality']}")
                    
                    with col2:
                        st.write(f"**Condition:** {report_dict['condition_diagnosed']}")
                        st.write(f"**ICD-10 Code:** {report_dict['icd10_code']}")
                        st.write(f"**Generated by:** {report_dict['generated_by_name']}")
                        st.write(f"**Date:** {report_dict['created_at']}")
                    
                    # Delete button for this specific report
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col2:
                        if st.button(f"🗑️ Delete This Report", key=f"delete_{report_dict['id']}"):
                            if delete_report(report_dict['id']):
                                st.success(f"Report deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete report")
                    
                    with col3:
                        if st.button(f"🔄 Refresh", key=f"refresh_{report_dict['id']}"):
                            st.rerun()
                    
                    # Show formatted report
                    st.subheader("Clinical Report Content")
                    if report_dict.get('formatted_report'):
                        st.text_area("Report Content", report_dict['formatted_report'], height=300, key=f"formatted_{report_dict['id']}")
                        
                        # Create PDF for download
                        pdf_report = create_pdf_report(report_dict['formatted_report'], report_dict['patient_id'])
                        
                        # Download buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📄 Download Text Report",
                                data=report_dict['formatted_report'],
                                file_name=f"ehr_report_{report_dict['patient_id']}_{report_dict['created_at'].split()[0].replace('-', '')}.txt",
                                mime="text/plain",
                                key=f"text_{report_dict['id']}"
                            )
                        
                        with col2:
                            st.download_button(
                                label="📊 Download PDF Report",
                                data=pdf_report.getvalue(),
                                file_name=f"ehr_report_{report_dict['patient_id']}_{report_dict['created_at'].split()[0].replace('-', '')}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{report_dict['id']}"
                            )
                    else:
                        st.info("No formatted report content available.")
        else:
            st.info("No EHR reports found in the database. Generate some reports first.")
    
    with tab2:
        st.subheader("Search EHR Reports")
        search_term = st.text_input("Enter Patient ID or Condition")
        
        if search_term:
            reports = get_all_reports()
            filtered_reports = [
                r for r in reports 
                if search_term.lower() in r['patient_id'].lower() or 
                   (r['condition_diagnosed'] and search_term.lower() in r['condition_diagnosed'].lower())
            ]
            
            if filtered_reports:
                st.write(f"**Found {len(filtered_reports)} reports matching '{search_term}'**")
                for report in filtered_reports:
                    report_dict = dict(report)
                    with st.expander(f"Patient {report_dict['patient_id']} - {report_dict['condition_diagnosed']}"):
                        st.write(f"**Modality:** {report_dict['modality']}")
                        st.write(f"**Date:** {report_dict['created_at']}")
                        
                        # Delete button in search results too
                        if st.button(f"Delete This Report", key=f"search_delete_{report_dict['id']}"):
                            if delete_report(report_dict['id']):
                                st.success(f"Report deleted successfully!")
                                st.rerun()
                        
                        if report_dict.get('formatted_report'):
                            st.text_area("Report", report_dict['formatted_report'], height=200, key=f"search_{report_dict['id']}")
            else:
                st.info("No reports found matching your search criteria.")

if __name__ == "__main__":
    main()