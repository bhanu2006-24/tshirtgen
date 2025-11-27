import streamlit as st
import qrcode
import io
import random
import string
import uuid
import json
from PIL import Image

st.set_page_config(page_title="Utilities", page_icon="🛠️", layout="wide")

st.title("🛠️ Utility Tools")
st.markdown("A collection of handy tools for everyday tasks.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["QR Code", "Password", "Converter", "Text", "Dev"])

# --- QR Code Generator ---
with tab1:
    st.header("📱 QR Code Generator")
    qr_text = st.text_input("Enter text or URL", "https://streamlit.io")
    qr_color = st.color_picker("Fill Color", "#000000")
    qr_bg = st.color_picker("Background Color", "#FFFFFF")
    
    if st.button("Generate QR Code"):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color=qr_color, back_color=qr_bg)
        
        # Convert to bytes for display/download
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.image(byte_im, caption="Generated QR Code", width=300)
        st.download_button("Download QR Code", data=byte_im, file_name="qrcode.png", mime="image/png")

# --- Password Generator ---
with tab2:
    st.header("🔐 Password Generator")
    length = st.slider("Length", 8, 64, 16)
    use_digits = st.checkbox("Include Digits", True)
    use_special = st.checkbox("Include Special Characters", True)
    
    if st.button("Generate Password"):
        chars = string.ascii_letters
        if use_digits:
            chars += string.digits
        if use_special:
            chars += string.punctuation
            
        password = ''.join(random.choice(chars) for _ in range(length))
        st.code(password, language="text")

# --- Unit Converter ---
with tab3:
    st.header("⚖️ Unit Converter")
    unit_type = st.selectbox("Type", ["Length", "Weight", "Temperature"])
    
    col1, col2, col3 = st.columns(3)
    
    if unit_type == "Length":
        with col1:
            val = st.number_input("Value", value=1.0)
        with col2:
            from_unit = st.selectbox("From", ["Meters", "Kilometers", "Feet", "Miles"])
        with col3:
            to_unit = st.selectbox("To", ["Meters", "Kilometers", "Feet", "Miles"])
            
        # Simple conversion logic (base: meters)
        factors = {"Meters": 1, "Kilometers": 1000, "Feet": 0.3048, "Miles": 1609.34}
        result = val * factors[from_unit] / factors[to_unit]
        st.metric("Result", f"{result:.4f} {to_unit}")
        
    elif unit_type == "Weight":
        with col1:
            val = st.number_input("Value", value=1.0)
        with col2:
            from_unit = st.selectbox("From", ["Kilograms", "Pounds", "Ounces"])
        with col3:
            to_unit = st.selectbox("To", ["Kilograms", "Pounds", "Ounces"])
            
        # Base: kg
        factors = {"Kilograms": 1, "Pounds": 0.453592, "Ounces": 0.0283495}
        result = val * factors[from_unit] / factors[to_unit]
        st.metric("Result", f"{result:.4f} {to_unit}")

    elif unit_type == "Temperature":
        with col1:
            val = st.number_input("Value", value=0.0)
        with col2:
            from_unit = st.selectbox("From", ["Celsius", "Fahrenheit", "Kelvin"])
        with col3:
            to_unit = st.selectbox("To", ["Celsius", "Fahrenheit", "Kelvin"])
            
        # Convert to C first
        if from_unit == "Fahrenheit": c_val = (val - 32) * 5/9
        elif from_unit == "Kelvin": c_val = val - 273.15
        else: c_val = val
        
        # Convert C to target
        if to_unit == "Fahrenheit": result = c_val * 9/5 + 32
        elif to_unit == "Kelvin": result = c_val + 273.15
        else: result = c_val
        
        st.metric("Result", f"{result:.2f} {to_unit}")

# --- Text Tools ---
with tab4:
    st.header("📝 Text Analyzer")
    text_input = st.text_area("Enter text to analyze", "Streamlit is awesome!")
    
    if text_input:
        c1, c2, c3 = st.columns(3)
        c1.metric("Characters", len(text_input))
        c2.metric("Words", len(text_input.split()))
        c3.metric("Lines", len(text_input.splitlines()))
        
        st.subheader("Case Converter")
        st.text(f"UPPER: {text_input.upper()}")
        st.text(f"lower: {text_input.lower()}")
        st.text(f"Title Case: {text_input.title()}")

# --- Dev Tools ---
with tab5:
    st.header("👨‍💻 Developer Tools")
    
    st.subheader("UUID Generator")
    if st.button("Generate UUIDs"):
        st.write(f"**UUID1:** `{uuid.uuid1()}`")
        st.write(f"**UUID4:** `{uuid.uuid4()}`")
        
    st.subheader("JSON Formatter")
    json_input = st.text_area("Paste JSON here", '{"name":"John", "age":30}')
    if st.button("Format JSON"):
        try:
            parsed = json.loads(json_input)
            st.json(parsed)
        except json.JSONDecodeError:
            st.error("Invalid JSON")
