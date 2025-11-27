import streamlit as st
import requests
import random

st.set_page_config(page_title="Fun Zone", page_icon="🎲", layout="wide")

st.title("🎲 Fun Zone")

tab1, tab2, tab3, tab4 = st.tabs(["Jokes & Trivia", "Predictions", "Cute Animals", "Activities"])

# --- Jokes & Trivia ---
with tab1:
    st.header("😂 Random Joke Generator")
    if st.button("Tell me a joke"):
        try:
            res = requests.get("https://official-joke-api.appspot.com/random_joke")
            data = res.json()
            st.write(f"**{data['setup']}**")
            st.write(f"*{data['punchline']}*")
        except:
            st.error("Couldn't fetch a joke :(")
            
    st.divider()
    
    st.header("🔢 Number Facts")
    num = st.number_input("Pick a number", value=42)
    if st.button("Get Fact"):
        try:
            res = requests.get(f"http://numbersapi.com/{num}")
            st.info(res.text)
        except:
            st.error("API Error")

# --- Predictions ---
with tab2:
    st.header("🔮 Name Predictions")
    name = st.text_input("Enter your name", "Bhanu")
    
    if st.button("Predict"):
        c1, c2, c3 = st.columns(3)
        
        # Agify
        try:
            res = requests.get(f"https://api.agify.io?name={name}").json()
            c1.metric("Predicted Age", res.get("age", "N/A"))
        except: c1.error("Error")
            
        # Genderize
        try:
            res = requests.get(f"https://api.genderize.io?name={name}").json()
            c2.metric("Predicted Gender", f"{res.get('gender', 'N/A')} ({res.get('probability', 0)*100:.0f}%)")
        except: c2.error("Error")
            
        # Nationalize
        try:
            res = requests.get(f"https://api.nationalize.io?name={name}").json()
            if res.get("country"):
                top_country = res["country"][0]["country_id"]
                c3.metric("Likely Nationality", top_country)
            else:
                c3.metric("Nationality", "Unknown")
        except: c3.error("Error")

# --- Cute Animals ---
with tab3:
    st.header("🐱🐶 Cute Animals")
    animal = st.radio("Choose your fighter", ["Cat", "Dog"])
    
    if st.button("Show me!"):
        if animal == "Cat":
            url = "https://api.thecatapi.com/v1/images/search"
        else:
            url = "https://api.thedogapi.com/v1/images/search"
            
        try:
            res = requests.get(url).json()
            st.image(res[0]["url"], width=400)
        except:
            st.error("Could not load image")

# --- Activities ---
with tab4:
    st.header("🥱 Bored?")
    st.write("Get an activity suggestion!")
    
    if st.button("I'm Bored"):
        try:
            res = requests.get("https://bored.api.lewagon.com/api/activity/")
            data = res.json()
            st.success(f"**Activity:** {data['activity']}")
            st.write(f"**Type:** {data['type']}")
            st.write(f"**Participants:** {data['participants']}")
        except:
            st.error("API Error")
