

Cleaning

Removed duplicate and corrupted image files.

Dropped incomplete/malformed rows in structured EHR datasets.

Standardization

Resized all images to 256×256 pixels.

Converted image formats to .png for consistency.

Normalized EHR text (lowercasing, punctuation cleanup).

Labeling

MRI & CT: Labels mapped to “Normal”, “Tumor”, “Cancer”.

X-ray: Labels mapped to “Normal” vs “Pneumonia”.

EHR: Diagnoses mapped to ICD-10 codes.

Tools Used

Python (Pandas, NumPy).

OpenCV & PIL (image resizing/conversion).

pdf plumber & regular expression


