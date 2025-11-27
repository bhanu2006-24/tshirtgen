import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Geo Info", page_icon="🌍", layout="wide")

st.title("🌍 Geographical & Weather Info")

tab1, tab2, tab3 = st.tabs(["Weather", "Country Info", "IP Lookup"])

# --- Weather ---
with tab1:
    st.header("🌤️ Weather Dashboard")
    city = st.text_input("Enter City Name", "London")
    
    if st.button("Get Weather"):
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        try:
            geo_res = requests.get(geo_url).json()
            if "results" in geo_res:
                lat = geo_res["results"][0]["latitude"]
                lon = geo_res["results"][0]["longitude"]
                name = geo_res["results"][0]["name"]
                country = geo_res["results"][0]["country"]
                
                st.success(f"Found: {name}, {country} ({lat}, {lon})")
                
                # 2. Weather Data
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
                w_res = requests.get(weather_url).json()
                
                curr = w_res["current_weather"]
                st.metric("Temperature", f"{curr['temperature']} °C", f"Wind: {curr['windspeed']} km/h")
                
                # Daily forecast chart
                daily = w_res["daily"]
                df = pd.DataFrame({
                    "Date": daily["time"],
                    "Max Temp": daily["temperature_2m_max"],
                    "Min Temp": daily["temperature_2m_min"]
                })
                
                fig = px.line(df, x="Date", y=["Max Temp", "Min Temp"], title="7-Day Forecast")
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("City not found!")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

# --- Country Info ---
with tab2:
    st.header("🏳️ Country Information")
    country_name = st.text_input("Enter Country Name", "Japan")
    
    if st.button("Search Country"):
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()[0]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.image(data["flags"]["png"], width=200)
                    st.subheader(data["name"]["common"])
                    st.write(f"**Capital:** {data.get('capital', ['N/A'])[0]}")
                    st.write(f"**Region:** {data['region']}")
                
                with c2:
                    st.write(f"**Population:** {data['population']:,}")
                    st.write(f"**Area:** {data['area']:,} km²")
                    currencies = ", ".join([c["name"] for c in data.get("currencies", {}).values()])
                    st.write(f"**Currency:** {currencies}")
                    
                # Map
                if "latlng" in data:
                    st.map(pd.DataFrame({'lat': [data['latlng'][0]], 'lon': [data['latlng'][1]]}))
            else:
                st.error("Country not found!")
        except Exception as e:
            st.error(f"Error: {e}")

# --- IP Lookup ---
with tab3:
    st.header("📍 IP Address Lookup")
    ip_addr = st.text_input("Enter IP Address (leave empty for yours)", "")
    
    if st.button("Lookup IP"):
        target = ip_addr if ip_addr else "json"
        url = f"https://ipapi.co/{target}/json/" if ip_addr else "https://ipapi.co/json/"
        
        try:
            res = requests.get(url, headers={"User-Agent": "streamlit-app"})
            data = res.json()
            
            if "error" in data:
                st.error(data["reason"])
            else:
                st.json(data)
                st.map(pd.DataFrame({'lat': [data.get('latitude', 0)], 'lon': [data.get('longitude', 0)]}))
        except Exception as e:
            st.error(f"Error: {e}")
