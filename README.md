# 🎽 Random T‑Shirt Style Generator

A playful Streamlit app that procedurally generates abstract “T‑shirt print” designs using **NumPy**, **OpenCV**, **Pillow**, **math**, **colorsys**, and randomness.  
It composes wild combinations of circles, squares, polygons, and lines with smart color palettes, gradients, noise textures, and text overlays — perfect for generating unique T‑shirt art.

---

## ✨ Features

- **Procedural art** with layered shapes: circles, squares, rectangles, polygons, lines
- **Smart color palettes**: random, complementary, triadic, analogous, monochrome
- **Base styles**: solid, vertical stripes, radial gradient, linear gradient, noise
- **Random seed** for reproducible results
- **Noise blending** for texture
- **Optional text overlay** with bold random words
- **Resolution control** (supports large canvases for print, e.g., 4500×5400 for 15×18" at 300 DPI)
- **Transparent background** option
- **Download as PNG**

---

## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/bhanu2006-24/tshirtgen
cd tshirt-style-generator

# Create a virtual environment (recommended)
conda create -n tshirtgen python=3.11
conda activate tshirtgen

# Install requirements
pip install -r requirements.txt
