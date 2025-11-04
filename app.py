import io
import math
import random
import colorsys
from typing import Tuple, List

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ---------------- Page config ----------------
st.set_page_config(page_title="🎽 Random T‑Shirt Style Generator", page_icon="🎨", layout="wide")

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.title("⚙️ Controls")
    seed_input = st.text_input("Seed (empty = random)", "")
    width = st.number_input("Canvas width (px)", min_value=512, max_value=8000, value=3000, step=100)
    height = st.number_input("Canvas height (px)", min_value=512, max_value=8000, value=3600, step=100)
    transparent_bg = st.checkbox("Transparent background", value=False)

    st.markdown("---")
    palette_mode = st.selectbox("Palette strategy", ["random", "complementary", "triadic", "analogous", "monochrome"], index=0)
    base_style = st.selectbox("Base style", ["solid", "vertical_stripes", "radial_gradient", "linear_gradient", "noise"], index=2)

    st.markdown("---")
    layers_count = st.slider("Shape layers", 3, 25, 12)
    add_text = st.checkbox("Add random text overlay", value=True)
    add_lines = st.checkbox("Add line splashes", value=True)
    add_blend_noise = st.checkbox("Blend extra noise", value=True)
    anti_alias = st.checkbox("Anti‑alias (slightly slower)", value=True)

    st.caption("Tip: For print, use large canvases (e.g., 4500×5400 for 15×18\" at 300 DPI).")

st.title("🎽 Random T‑Shirt Style Generator")
st.markdown("Generate abstract, colorful T‑shirt print styles with procedural shapes, gradients, and noise. Use the seed to reproduce designs.")

# ---------------- Utilities ----------------
def set_seed(seed_text: str):
    if seed_text.strip():
        try:
            seed_val = int(seed_text.strip())
        except ValueError:
            seed_val = abs(hash(seed_text)) % (2**32)
    else:
        seed_val = random.randint(0, 2**32 - 1)
    random.seed(seed_val)
    np.random.seed(seed_val)
    return seed_val

def clamp01(x):
    """Clamp scalar or numpy array to [0,1]."""
    return np.clip(x, 0.0, 1.0)

def to_rgb_tuple(h, s, v) -> Tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def build_palette(mode: str, base_h=None) -> List[Tuple[int, int, int]]:
    if base_h is None:
        base_h = random.random()
    s = 0.7 + 0.3 * random.random()
    v = 0.8 + 0.2 * random.random()
    palette = []

    if mode == "complementary":
        palette = [to_rgb_tuple(base_h, s, v), to_rgb_tuple((base_h + 0.5) % 1.0, s, v)]
    elif mode == "triadic":
        palette = [
            to_rgb_tuple(base_h, s, v),
            to_rgb_tuple((base_h + 1/3) % 1.0, s, v),
            to_rgb_tuple((base_h + 2/3) % 1.0, s, v),
        ]
    elif mode == "analogous":
        offsets = [-0.08, -0.04, 0.0, 0.04, 0.08]
        palette = [to_rgb_tuple((base_h + o) % 1.0, s, v) for o in offsets]
    elif mode == "monochrome":
        vs = [0.35, 0.55, 0.75, 0.9]
        palette = [to_rgb_tuple(base_h, s, v_) for v_ in vs]
    else:  # random
        palette = [to_rgb_tuple(random.random(), 0.6 + 0.4 * random.random(), 0.6 + 0.4 * random.random()) for _ in range(5)]
    return palette

def np_to_pil(arr: np.ndarray, mode="RGBA") -> Image.Image:
    return Image.fromarray(arr, mode)

def pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img)

def make_base(width: int, height: int, style: str, transparent: bool) -> Image.Image:
    if transparent:
        base = np.zeros((height, width, 4), dtype=np.uint8)
    else:
        base = np.zeros((height, width, 3), dtype=np.uint8)
        base[:] = (255, 255, 255)

    if style == "solid":
        pass
    elif style == "radial_gradient":
        cx, cy = width / 2, height / 2
        yy, xx = np.mgrid[0:height, 0:width]
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2) / np.sqrt(cx**2 + cy**2)
        t = (1 - clamp01(dist))**1.2
        c1 = np.array([random.randint(0, 255) for _ in range(3)], dtype=np.float32)
        c2 = np.array([random.randint(0, 255) for _ in range(3)], dtype=np.float32)
        grad = (c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]).astype(np.uint8)
        base[..., :3] = grad
        if transparent and base.shape[-1] == 4:
            base[..., 3] = 255
    elif style == "linear_gradient":
        yy, xx = np.mgrid[0:height, 0:width]
        t = clamp01(xx / width)
        c1 = np.array([random.randint(0, 255) for _ in range(3)], dtype=np.float32)
        c2 = np.array([random.randint(0, 255) for _ in range(3)], dtype=np.float32)
        grad = (c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]).astype(np.uint8)
        base[..., :3] = grad
        if transparent and base.shape[-1] == 4:
            base[..., 3] = 255
    elif style == "noise":
        noise = (np.random.rand(height, width, 3) * 255).astype(np.uint8)
        base[..., :3] = cv2.GaussianBlur(noise, (0, 0), sigmaX=1.2, sigmaY=1.2)
        if transparent and base.shape[-1] == 4:
            base[..., 3] = 255

    mode = "RGBA" if base.shape[-1] == 4 else "RGB"
    return np_to_pil(base, mode=mode)

# ---------------- Shape drawing ----------------
def draw_shapes(img: Image.Image, palette: List[Tuple[int, int, int]], layers: int):
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for _ in range(layers):
        color = random.choice(palette)
        a = random.randint(100, 200)
        fill = (*color, a)
        shape_type = random.choice(["circle", "square", "rect", "poly", "line"])
        cx, cy = random.randint(0, w), random.randint(0, h)
        size = random.randint(int(0.05 * min(w, h)), int(0.35 * min(w, h)))

        if shape_type == "circle":
            bbox = [cx - size, cy - size, cx + size, cy + size]
            draw.ellipse(bbox, fill=fill)
        elif shape_type == "square":
            bbox = [cx - size, cy - size, cx + size, cy + size]
            draw.rectangle(bbox, fill=fill)
        elif shape_type == "rect":
            w2 = size * random.uniform(0.6, 1.6)
            h2 = size * random.uniform(0.4, 1.4)
            bbox = [int(cx - w2), int(cy - h2), int(cx + w2), int(cy + h2)]
            draw.rectangle(bbox, fill=fill)
        elif shape_type == "poly":
            n = random.randint(3, 8)
            pts = []
            for i in range(n):
                ang = 2 * math.pi * i / n + random.uniform(-0.2, 0.2)
                r = size * random.uniform(0.6, 1.2)
                px = int(cx + r * math.cos(ang))
                py = int(cy + r * math.sin(ang))
                pts.append((px, py))
            draw.polygon(pts, fill=fill)

        elif shape_type == "line":
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            x2 = random.randint(0, w)
            y2 = random.randint(0, h)
            stroke = (*color, 255)
            thickness = random.randint(2, 8)
            draw.line([(x1, y1), (x2, y2)], fill=stroke, width=thickness)

# ---------------- Noise & text overlays ----------------
def blend_noise(img: Image.Image, strength: float = 0.25):
    """Blend random noise into the image for texture."""
    arr = pil_to_np(img).astype(np.float32)
    noise = (np.random.rand(*arr.shape[:2], 3) * 255).astype(np.float32)
    arr[..., :3] = (1 - strength) * arr[..., :3] + strength * noise
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if arr.shape[-1] == 4:
        arr[..., 3] = pil_to_np(img)[..., 3]
    mode = "RGBA" if arr.shape[-1] == 4 else "RGB"
    return np_to_pil(arr, mode)

def add_text_overlay(img: Image.Image, palette: List[Tuple[int, int, int]]):
    """Overlay random bold text onto the design."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    w, h = img.size
    text = random.choice(["VIBE", "RAW", "WAVE", "BOLD", "MOTION", "EDGE"])
    color = random.choice(palette)
    alpha = random.randint(160, 220)
    fill = (*color, alpha)

    size = int(min(w, h) * random.uniform(0.08, 0.18))
    try:
        font = ImageFont.truetype("Arial.ttf", size=size)
    except:
        font = ImageFont.load_default()

    tx = random.randint(int(0.1 * w), int(0.8 * w))
    ty = random.randint(int(0.1 * h), int(0.8 * h))
    angle = random.randint(-25, 25)

    # Create overlay
    temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dtemp = ImageDraw.Draw(temp)
    dtemp.text((tx, ty), text, font=font, fill=fill)

    # Rotate overlay separately
    temp = temp.rotate(angle, resample=Image.BICUBIC, center=(tx, ty), expand=False)

    # Composite safely
    img = Image.alpha_composite(img, temp)
    return img

def scale_for_antialias(img: Image.Image, aa: bool) -> Image.Image:
    """Optionally render larger and downsample for smoother edges."""
    if not aa:
        return img
    w, h = img.size
    big = img.resize((int(w * 1.5), int(h * 1.5)), Image.BICUBIC)
    return big.resize((w, h), Image.LANCZOS)

# ---------------- Main generate ----------------
seed_value = set_seed(seed_input)
st.caption(f"Seed: {seed_value}")

generate = st.button("🎲 Generate")
if generate:
    with st.spinner("Crafting your T‑shirt art..."):
        # Base background
        base = make_base(width, height, base_style, transparent_bg)

        # Palette
        palette = build_palette(palette_mode)

        # Shapes
        draw_shapes(base, palette, layers_count)

        # Extra line splashes with OpenCV
        if add_lines:
            arr = pil_to_np(base)
            for _ in range(random.randint(6, 14)):
                x1, y1 = random.randint(0, width-1), random.randint(0, height-1)
                x2, y2 = random.randint(0, width-1), random.randint(0, height-1)
                color = random.choice(palette)
                thickness = random.randint(2, 10)
                if arr.shape[-1] == 4:
                    cv2.line(arr[..., :3], (x1, y1), (x2, y2), color, thickness, lineType=cv2.LINE_AA)
                else:
                    cv2.line(arr, (x1, y1), (x2, y2), color, thickness, lineType=cv2.LINE_AA)
            base = np_to_pil(arr, "RGBA" if arr.shape[-1] == 4 else "RGB")

        # Blend noise
        if add_blend_noise:
            base = blend_noise(base, strength=random.uniform(0.15, 0.35))

        # Text overlay
        if add_text:
            base = add_text_overlay(base, palette)

        # Anti‑alias finishing
        base = scale_for_antialias(base, anti_alias)

        # Preview
        st.image(base, caption="Generated design", use_container_width=True)

        # Download
        buf = io.BytesIO()
        base.save(buf, format="PNG")
        buf.seek(0)
        st.download_button(
            "⬇️ Download PNG",
            data=buf,
            file_name=f"tshirt_style_{seed_value}.png",
            mime="image/png"
        )

else:
    st.info("Click ‘Generate’ to create a fresh design. Use a seed to reproduce results.")
