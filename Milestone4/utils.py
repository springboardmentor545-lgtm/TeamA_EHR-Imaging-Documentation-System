import re
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def load_master_metadata():
    """Load master metadata CSV file"""
    try:
        df = pd.read_csv('master_metadata.csv')
        return df
    except FileNotFoundError:
        st.error("master_metadata.csv file not found. Please ensure it's in the same directory.")
        return pd.DataFrame()

def clean_text(text):
    """Clean and format text output"""
    text = text.replace('*', '').replace('★', '')
    text = re.sub(r'\n\s*\n', '\n\n', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() == '':
            cleaned_lines.append('')
        else:
            cleaned_lines.append(' '.join(line.split()))
    return '\n'.join(cleaned_lines)

def process_cardiac_imaging_data(patient_studies, patient_id):
    """Main pipeline for processing cardiac imaging data"""
    from image_processing import (
        build_srcnn_model, build_classification_model, 
        load_and_process_slices, enhance_with_srcnn, 
        extract_image_features, validate_image_slices
    )
    from report_generator import classify_cardiac_condition, generate_cardiac_report
    
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
            
            # Validate slices
            validation = validate_image_slices(slices)
            if validation['valid_slices'] == 0:
                st.error(f"No valid slices found for {modality}. Skipping analysis.")
                continue
                
            st.info(f"Validated {validation['valid_slices']}/{validation['total_slices']} slices")
            
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

def get_feature_statistics(image_features):
    """Get statistics for image features"""
    if not image_features:
        return {}
    
    feature_names = ['mean_intensity', 'std_intensity', 'contrast', 'entropy', 
                    'homogeneity', 'cardiac_area', 'symmetry_score']
    
    stats = {}
    for feature in feature_names:
        values = [f[feature] for f in image_features if feature in f]
        if values:
            stats[feature] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
    
    return stats