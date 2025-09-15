📌 Project Overview

This project focuses on enhancing medical images (MRI, CT, X-ray) using Generative AI and classical deep learning models. The goal is to improve image clarity, denoise scans, and provide healthcare professionals with diagnostic-quality visuals.

Milestone 2 covers implementation, experimentation, and evaluation of image enhancement techniques.
📂 Folder Structure

Milestone2/

│|    

|├── Documentation   # Reports, milestone documentation, write-ups

|├── Presentation    # PPT files summarizing the milestone

|├── Projectfile     # Source code, preprocessing, and model scripts

|├── Resources       # Reference papers, notes, datasets (links if large)

|└── Results         # Enhanced vs original images, zipped outputs

✅ Steps Completed in Milestone 2
1. Dataset Preparation

Collected MRI, CT, and X-ray images.

Selected ~20–50 images for testing enhancement.

2. Preprocessing

Standardized formats: .png, resized to 256x256.

Normalized pixel values to range 0.0 – 1.0.

Created train/test split.

3. Enhancement Techniques Applied

Classical Deep Models: DnCNN, EDSR, SRCNN.

Generative AI-based: API-based denoising & upscaling.

OpenCV Methods: Backup sharpening & noise reduction.

4. Validation

Compared before vs. after images.

Metrics used: PSNR (Peak Signal-to-Noise Ratio), SSIM (Structural Similarity Index).

Results stored in /Results folder.

5. Challenges Faced

Slow CPU training → shifted to Colab GPU.

Some models produced blurry outputs.

Handling large result sets (~100 images) was difficult.

Used OpenCV methods when deep models underperformed.

📊 Results

Enhanced images show better clarity and sharpness.

Visual evaluation proved more reliable than metrics (due to limited ground-truth HQ images).

Hybrid approach (Classical + GenAI) achieved the best overall results.
