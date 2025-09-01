# Chest X-Ray Pneumonia Classification AI Project

## Module 1: Data Collection and Preprocessing

This project prepares a dataset of chest X-ray images to train an AI model to detect pneumonia.

### Dataset Source
- **Name:** Chest X-Ray Images (Pneumonia)
- **Source:** [Kaggle] (https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)
- **Total Images:** 5,856
- **Classes:** NORMAL, PNEUMONIA

### Preprocessing Steps
1.  **Exploratory Data Analysis (EDA):** Discovered class imbalance (4273 PNEUMONIA vs 1583 NORMAL) and varying image sizes.
2.  **Data Cleaning:** Organized all images into a structured pandas DataFrame.
3.  **Data Standardization:** Resized all images to 224x224 pixels and normalized pixel values to [0, 1].
4.  **Data Splitting:** Split data into Train (3747), Validation (937), and Test (1172) sets.

### Sample Images
The `sample_data` folder contains 80 example images (40 from each class) from the test set.

### Sample Images
The `sample_data.zip` file contains 80 example images (40 from each class) from the test set. Download and unzip this file to view the images.

### How to Reproduce
1.  Download the dataset from Kaggle.
2.  Place the unzipped `chest_xray` folder inside a `data/archive/` directory.

3.  Run the `chest_xray_analysis.ipynb` notebook to reproduce the preprocessing.
