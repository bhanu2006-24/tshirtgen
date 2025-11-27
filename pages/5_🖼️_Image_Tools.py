import streamlit as st
from PIL import Image, ImageFilter, ImageOps
import io

st.set_page_config(page_title="Image Tools", page_icon="🖼️", layout="wide")

st.title("🖼️ Image Tools")

tab1, tab2, tab3 = st.tabs(["Filters", "Resizer", "Metadata"])

uploaded_file = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Original Image", use_container_width=True)

# --- Filters ---
with tab1:
    st.header("🎨 Image Filters")
    
    if uploaded_file:
        filter_type = st.selectbox("Choose Filter", ["None", "Blur", "Contour", "Detail", "Edge Enhance", "Grayscale", "Invert"])
        
        if filter_type != "None":
            if filter_type == "Blur":
                processed = image.filter(ImageFilter.BLUR)
            elif filter_type == "Contour":
                processed = image.filter(ImageFilter.CONTOUR)
            elif filter_type == "Detail":
                processed = image.filter(ImageFilter.DETAIL)
            elif filter_type == "Edge Enhance":
                processed = image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == "Grayscale":
                processed = ImageOps.grayscale(image)
            elif filter_type == "Invert":
                # Invert needs RGB/L mode
                if image.mode == 'RGBA':
                    r,g,b,a = image.split()
                    rgb_image = Image.merge('RGB', (r,g,b))
                    inverted_image = ImageOps.invert(rgb_image)
                    r2,g2,b2 = inverted_image.split()
                    processed = Image.merge('RGBA', (r2,g2,b2,a))
                else:
                    processed = ImageOps.invert(image.convert('RGB'))
            
            st.image(processed, caption=f"{filter_type} Filter", use_container_width=True)
            
            # Download
            buf = io.BytesIO()
            processed.save(buf, format="PNG")
            st.download_button("Download Processed Image", data=buf.getvalue(), file_name=f"filtered_{filter_type}.png", mime="image/png")
        else:
            st.image(image, use_container_width=True)
    else:
        st.info("Upload an image to get started!")

# --- Resizer ---
with tab2:
    st.header("📏 Image Resizer")
    
    if uploaded_file:
        c1, c2 = st.columns(2)
        with c1:
            new_width = st.number_input("Width", value=image.width)
        with c2:
            new_height = st.number_input("Height", value=image.height)
            
        if st.button("Resize"):
            resized = image.resize((new_width, new_height))
            st.image(resized, caption=f"Resized to {new_width}x{new_height}", width=new_width if new_width < 700 else None)
            
            buf = io.BytesIO()
            resized.save(buf, format="PNG")
            st.download_button("Download Resized Image", data=buf.getvalue(), file_name=f"resized_{new_width}x{new_height}.png", mime="image/png")
    else:
        st.info("Upload an image to get started!")

# --- Metadata ---
with tab3:
    st.header("ℹ️ Metadata (Exif)")
    
    if uploaded_file:
        st.write(f"**Format:** {image.format}")
        st.write(f"**Mode:** {image.mode}")
        st.write(f"**Size:** {image.size}")
        
        exif_data = image._getexif()
        if exif_data:
            st.json(str(exif_data))
        else:
            st.warning("No EXIF data found.")
    else:
        st.info("Upload an image to get started!")
