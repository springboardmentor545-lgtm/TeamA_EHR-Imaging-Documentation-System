# utils.py
import numpy as np
import pandas as pd
import cv2
import re
import yaml
from scipy.ndimage import generic_filter
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Conv2D, Input, Flatten, Dense, Dropout, MaxPooling2D

# --- Load Configuration ---
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

ICD10_CODES = config['ICD10_CODES']
RISK_THRESHOLDS = config['RISK_THRESHOLDS']


def clean_text(text):
    """Removes unwanted characters and cleans up whitespace from generated text."""
    text = text.replace('*', '').replace('★', '')

    # Replace multiple newlines with single ones (keeping structured format)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() == '':
            cleaned_lines.append('')
        else:
            # Normalize internal spacing in lines
            cleaned_lines.append(' '.join(line.split()))

    return '\n'.join(cleaned_lines)

# --- Model Building Functions ---

def build_srcnn_model():
    """Builds the Super-Resolution Convolutional Neural Network (SRCNN) model."""
    input_img = Input(shape=(None, None, 1))
    
    # Layer 1: Feature extraction (9x9)
    x = Conv2D(64, (9, 9), padding='same', activation='relu')(input_img)
    # Layer 2: Non-linear mapping (1x1)
    x = Conv2D(32, (1, 1), padding='same', activation='relu')(x)
    # Layer 3: Reconstruction (5x5)
    output = Conv2D(1, (5, 5), padding='same', activation='linear')(x)

    model = Model(input_img, output)
    model.compile(optimizer=config['SRCNN_OPTIMIZER'], loss=config['SRCNN_LOSS'])
    return model

def build_classification_model(input_shape=config['CLASSIFICATION_INPUT_SHAPE']):
    """
    Builds the CNN model for cardiac image classification.
    NOTE: This model is defined but not trained in the provided pipeline.
    """
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
        Dense(config['CLASSIFICATION_OUTPUT_CLASSES'], activation='softmax')
    ])

    model.compile(optimizer=config['CLASSIFICATION_OPTIMIZER'],
                  loss=config['CLASSIFICATION_LOSS'],
                  metrics=config['CLASSIFICATION_METRICS'])
    return model

# --- Image Processing and Feature Calculation ---

def load_and_process_slices(folder_path, num_slices, target_size=config['IMAGE_TARGET_SIZE']):
    """
    Simulates loading and processing of cardiac image slices.
    In this version, it generates synthetic image data.
    """
    processed_slices = []
    for i in range(num_slices):
        # Base synthetic image (darker background)
        synthetic_img = np.random.rand(target_size[0], target_size[1]) * 0.5
        center_x, center_y = target_size[0] // 2, target_size[1] // 2
        radius = min(target_size) // 3

        # Create a central 'heart' shape (brighter circle)
        y, x = np.ogrid[:target_size[0], :target_size[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        synthetic_img[mask] += 0.4
        synthetic_img = np.clip(synthetic_img, 0, 1)

        # Add simulated 'abnormalities' (lines/scars) every few slices
        if i % 3 == 0:
            cv2.line(synthetic_img, (center_x-30, center_y-20), (center_x+30, center_y-30), 0.8, 2)
            cv2.line(synthetic_img, (center_x-20, center_y+30), (center_x+25, center_y+25), 0.8, 2)

        processed_slices.append(synthetic_img)

    return processed_slices

def enhance_with_srcnn(slices, srcnn_model):
    """Enhances image slices using the pre-built SRCNN model."""
    enhanced_slices = []
    for slice in slices:
        # Prepare slice for model (add batch and channel dimensions)
        slice_expanded = np.expand_dims(slice, axis=0)
        slice_expanded = np.expand_dims(slice_expanded, axis=-1)
        
        # Predict the enhanced image
        enhanced = srcnn_model.predict(slice_expanded, verbose=0)
        enhanced = np.squeeze(enhanced)
        enhanced_slices.append(enhanced)
    return enhanced_slices

def calculate_entropy(image):
    """Calculates the entropy (randomness) of an image's intensity distribution."""
    # Create histogram, normalize to get probability distribution
    hist = np.histogram(image, bins=256, range=(0, 1))[0]
    hist = hist / hist.sum()
    # Calculate Shannon Entropy
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    return entropy

def calculate_homogeneity(image):
    """Estimates local homogeneity (smoothness) of the image."""
    # Use generic_filter with std deviation to get local variance/texture
    std_dev = generic_filter(image, np.std, size=5)
    # Homogeneity is inversely related to mean texture variation
    homogeneity = 1 / (1 + np.mean(std_dev))
    return homogeneity

def calculate_symmetry(image):
    """Calculates the symmetry score between the left and flipped right halves."""
    height, width = image.shape
    left_half = image[:, :width//2]
    right_half = image[:, width//2:]

    # Flip the right half horizontally
    right_flipped = np.fliplr(right_half)

    if left_half.shape == right_flipped.shape:
        # Mean Squared Error (MSE) between the two halves
        mse = np.mean((left_half - right_flipped) ** 2)
        # Symmetry is 1 / (1 + MSE) - closer to 1 means more symmetric
        symmetry = 1 / (1 + mse)
        return symmetry
    return 0.5 # Return neutral score if shapes don't match (e.g., odd width)

def estimate_cardiac_area(image):
    """Estimates the area of the largest object (simulated heart) via segmentation."""
    # Convert float image (0-1) to 8-bit for OpenCV processing (0-255)
    img_8bit = (image * 255).astype(np.uint8)
    
    # Use Otsu's thresholding to get a binary mask
    _, thresh = cv2.threshold(img_8bit, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assumed to be the heart)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        # Return area as a fraction of the total image size
        return area / (image.shape[0] * image.shape[1])
    return 0

def extract_image_features(slices):
    """Calculates a set of descriptive features for each image slice."""
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

# --- Classification Logic ---

def classify_cardiac_condition(image_features, age, gender, modality):
    """
    Classifies cardiac condition using a rule-based risk scoring system.
    This function replaces the need for a trained model in this pipeline.
    """
    risk_score = 0
    
    # Calculate average features across all slices
    avg_contrast = np.mean([f['contrast'] for f in image_features])
    avg_entropy = np.mean([f['entropy'] for f in image_features])
    avg_area = np.mean([f['cardiac_area'] for f in image_features])
    avg_symmetry = np.mean([f['symmetry_score'] for f in image_features])

    # Assign risk points based on image features
    if avg_contrast > 0.7:
        risk_score += 0.2
    if avg_entropy > 5:
        risk_score += 0.2
    if avg_area < 0.1 or avg_area > 0.4:  # Too small (atrophy) or too large (enlargement)
        risk_score += 0.2
    if avg_symmetry < 0.6:  # Low symmetry (structural deformation)
        risk_score += 0.2

    # Assign risk points based on patient demographics
    if age > 60:
        risk_score += 0.2
    elif age > 40:
        risk_score += 0.1
    if gender == 'M':
        risk_score += 0.1

    # Assign minor risk points based on modality used (MRI often highlights pathology better)
    if modality == 'CT':
        risk_score += 0.05
    elif modality == 'MRI':
        risk_score += 0.1

    # Determine condition based on cumulative risk score
    if risk_score < RISK_THRESHOLDS['NORMAL']:
        return 'normal', ICD10_CODES['normal']
    elif risk_score < RISK_THRESHOLDS['CORONARY_ARTERY_DISEASE']:
        return 'coronary_artery_disease', ICD10_CODES['coronary_artery_disease']
    elif risk_score < RISK_THRESHOLDS['ARRHYTHMIA']:
        return 'arrhythmia', ICD10_CODES['arrhythmia']
    elif risk_score < RISK_THRESHOLDS['CARDIOMYOPATHY']:
        return 'cardiomyopathy', ICD10_CODES['cardiomyopathy']
    else:
        return 'myocardial_infarction', ICD10_CODES['myocardial_infarction']

def generate_cardiac_report(patient_id, modality, condition, icd10_code, image_features, age, gender):
    """
    Generates a structured dictionary containing all report elements (findings, recommendations).
    """
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

    # --- Condition-Specific Logic ---
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

    # --- Demographic/Modality-Specific Logic ---
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

    # --- Final Report Structure ---
    report = {
        "patient_id": patient_id,
        "modality": modality,
        "age": age,
        "gender": gender,
        "condition_diagnosed": condition,
        "icd10_code": icd10_code,
        "image_characteristics": avg_features,
        "findings": findings,
        "recommendations": recommendations,
        "report_generated_by": config['REPORT_SYSTEM_VERSION']
    }

    return report
