📌 Project Overview

This project focuses on enhancing medical images (MRI, CT, X-ray) using Generative AI and classical deep learning models. The aim is to improve image clarity, denoise scans, and assist healthcare professionals with better diagnostic-quality visuals.

Milestone 2 primarily deals with implementation, experimentation, and evaluation of image enhancement techniques.

📂 Folder Structure
Milestone2/
│
├── Documentation   # Reports, milestone documentation, write-ups
├── Presentation    # PPT files summarizing the milestone
├── Projectfile     # Source code, preprocessing, and model scripts
├── Resources       # Reference papers, notes, datasets (links if large)
└── Results         # Enhanced vs original images, zipped outputs

✅ Steps Completed in Milestone 2

1.Dataset Preparation

Collected MRI, CT, and X-ray images.

Selected ~20–50 images for testing enhancement.

2.Preprocessing

Standardized formats (.png, 256x256).

Normalized pixel values (0.0 – 1.0).

Train/test split created.

3.Enhancement Techniques Applied

Classical Models: DnCNN, EDSR, SRCNN.

Generative AI-based: Used APIs to denoise and upscale.

OpenCV Methods: Backup for sharpening and noise reduction.

4.Validation

Compared before vs after images.

Metrics: PSNR (Peak Signal-to-Noise Ratio), SSIM (Structural Similarity Index).

Stored results in /Results folder.

5.Challenges Faced

CPU training was slow → Colab GPU used.

Blurry outputs from some models.

Difficulty handling large result sets (~100 images).

Fall back to OpenCV methods when deep models failed.

📊 Results

- Enhanced images show better clarity and sharpness.

- Visual evaluation more reliable than metrics (since ground truth HQ images were limited).

- Hybrid approach (Classical + GenAI) gave best results.
