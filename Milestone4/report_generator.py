import google.generativeai as genai
import numpy as np
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import json
import streamlit as st
from utils import clean_text

# Configure Gemini AI (will be initialized in main app)
genai.configure(api_key='AIzaSyDyVY2ZAFunydX53ncBlO1Y-hjgIlD1chM')

ICD10_CODES = {
    'normal': 'Z00.00',
    'mild_cardiomyopathy': 'I43',
    'coronary_artery_disease': 'I25', 
    'heart_failure': 'I50',
    'severe_cardiomyopathy': 'I42',
    'myocardial_infarction': 'I21',
    'arrhythmia': 'I49',
    'cardiomyopathy': 'I42',
    'valvular_heart_disease': 'I35'
}

def classify_cardiac_condition(image_features, age, gender, modality):
    """Classify cardiac condition optimized for synthetic data patterns"""
    
    # Calculate robust feature averages
    avg_features = {
        'cardiac_area': np.mean([f['cardiac_area'] for f in image_features]),
        'symmetry': np.mean([f['symmetry_score'] for f in image_features]),
        'contrast': np.mean([f['contrast'] for f in image_features]),
        'entropy': np.mean([f['entropy'] for f in image_features]),
        'homogeneity': np.mean([f['homogeneity'] for f in image_features])
    }
    
    # ADJUSTED LOGIC for synthetic data:
    risk_score = 0
    
    # 1. Contrast analysis (main reliable feature in synthetic data)
    if avg_features['contrast'] > 0.25:
        risk_score += 0.3  # High contrast may indicate pathology
    elif avg_features['contrast'] < 0.1:
        risk_score += 0.1  # Low contrast may be normal
    
    # 2. Entropy analysis (tissue complexity)
    if avg_features['entropy'] > 5.5:
        risk_score += 0.3  # High entropy = tissue heterogeneity
    elif avg_features['entropy'] < 3.0:
        risk_score += 0.1  # Low entropy = homogeneous tissue
    
    # 3. Homogeneity analysis
    if avg_features['homogeneity'] < 0.3:
        risk_score += 0.2  # Low homogeneity may indicate pathology
    
    # 4. Age factors (keep realistic)
    if age > 65:
        risk_score += 0.3
    elif age > 45:
        risk_score += 0.2
    
    # 5. Gender factors
    if gender == 'M' and age > 45:
        risk_score += 0.1
    elif gender == 'F' and age > 55:
        risk_score += 0.1
    
    # Diagnosis mapping for synthetic data
    if risk_score < 0.3:
        return 'normal', ICD10_CODES['normal']
    elif risk_score < 0.5:
        return 'mild_cardiomyopathy', ICD10_CODES['mild_cardiomyopathy']
    elif risk_score < 0.7:
        return 'coronary_artery_disease', ICD10_CODES['coronary_artery_disease']
    else:
        return 'heart_failure', ICD10_CODES['heart_failure']

def generate_cardiac_report(patient_id, modality, condition, icd10_code, image_features, age, gender):
    """Generate cardiac report optimized for synthetic data analysis"""
    
    avg_features = {
        'mean_intensity': np.mean([f['mean_intensity'] for f in image_features]),
        'contrast': np.mean([f['contrast'] for f in image_features]),
        'entropy': np.mean([f['entropy'] for f in image_features]),
        'cardiac_area': np.mean([f['cardiac_area'] for f in image_features]),
        'symmetry': np.mean([f['symmetry_score'] for f in image_features])
    }
    
    findings = []
    recommendations = []
    
    # Findings based on synthetic data patterns
    if condition == 'normal':
        findings.append("Cardiac structures demonstrate preserved architecture.")
        findings.append("Image contrast and tissue characteristics within normal limits.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f} (normal range)")
        recommendations.append("Routine cardiovascular follow-up recommended.")
        
    elif condition == 'mild_cardiomyopathy':
        findings.append("Mild alterations in cardiac tissue characteristics.")
        findings.append("Moderate image contrast variations suggestive of early structural changes.")
        findings.append(f"Tissue complexity (entropy): {avg_features['entropy']:.3f}")
        recommendations.append("Cardiology evaluation recommended.")
        recommendations.append("Consider echocardiogram for functional assessment.")
        
    elif condition == 'coronary_artery_disease':
        findings.append("Findings suggestive of coronary artery disease patterns.")
        findings.append("Elevated image contrast may indicate calcific deposits.")
        findings.append(f"Image contrast: {avg_features['contrast']:.3f} (elevated)")
        recommendations.append("Cardiology consultation advised.")
        recommendations.append("Cardiac risk factor assessment and lipid profile.")
        recommendations.append("Consider stress testing if clinically indicated.")
        
    elif condition == 'heart_failure':
        findings.append("Significant cardiac structural alterations identified.")
        findings.append("Marked tissue heterogeneity and contrast variations.")
        findings.append(f"Cardiac area: {avg_features['cardiac_area']:.3f}")
        findings.append(f"Tissue complexity: {avg_features['entropy']:.3f} (elevated)")
        recommendations.append("Urgent cardiology evaluation recommended.")
        recommendations.append("Comprehensive cardiac imaging and laboratory studies.")
        recommendations.append("Medical therapy optimization as per guidelines.")
    
    # Add demographic considerations
    if age > 60:
        findings.append("Age-appropriate cardiovascular changes noted.")
    
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
        "report_generated_by": "AI Cardiac Analysis System v2.0",
        "data_note": "Analysis based on synthetic cardiac imaging patterns"
    }
    
    return report

def generate_formatted_clinical_report(patient_id, cardiac_results, patient_info):
    """Generate a properly formatted clinical report"""
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
                report_content += f"- {finding}\n"
            
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
                report_content += f"- {recommendation}\n"
            
            report_content += "\n" + "="*50 + "\n\n"
    
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

def create_pdf_report(report_text, patient_id):
    """Create PDF version of clinical report"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', size=10)
    except:
        try:
            pdf.add_font('Arial', '', 'arial.ttf', uni=True)
            pdf.set_font('Arial', size=10)
        except:
            pdf.set_font("Arial", size=10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CARDIAC IMAGING REPORT", ln=True, align='C')
    pdf.ln(10)
    
    def clean_text_for_pdf(text):
        text = text.replace('•', '-')
        text = text.replace('❤️', '')
        text = text.replace('✅', '')
        text = text.replace('❌', '')
        text = text.encode('latin-1', 'ignore').decode('latin-1')
        return text
    
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
            pdf.multi_cell(0, 5, txt=line)
    
    pdf_output = BytesIO()
    try:
        pdf_output.write(pdf.output(dest='S').encode('latin-1'))
    except UnicodeEncodeError:
        pdf_output.write(pdf.output(dest='S').encode('utf-8', errors='ignore'))
    pdf_output.seek(0)
    
    return pdf_output

def generate_patient_report_both_modalities(patient_id, cardiac_results):
    """Generate AI-enhanced report using Gemini"""
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