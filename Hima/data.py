import pandas as pd
import os
from PIL import Image
import matplotlib.pyplot as plt

# Path to your folder
image_dir = r"C:\Users\Anjuri Hima\Downloads\archive (2)\The IQ-OTHNCCD lung cancer dataset\The IQ-OTHNCCD lung cancer dataset\Normal cases"

# List all files
files = os.listdir(image_dir)

# Create DataFrame
df = pd.DataFrame({
    "filename": files,
    "filepath": [os.path.join(image_dir, f) for f in files]
})

print("Total images:", len(df))

# Show first 5 images
for i in range(5):
    img_path = df["filepath"][i]
    img = Image.open(img_path)

    plt.imshow(img, cmap="gray")   # use cmap="gray" for X-rays/CT scans
    plt.title(df["filename"][i])
    plt.axis("off")
    plt.show()
