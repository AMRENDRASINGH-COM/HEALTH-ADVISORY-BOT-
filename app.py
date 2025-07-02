import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import time

# --- Bulletproof Configuration ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")

if not API_KEY:
    st.error("❌ Missing API Key. Add GOOGLE_API_KEY to your .env file")
    st.stop()

# Try both API endpoints
ENDPOINTS = [
    'https://generativelanguage.googleapis.com/v1',
    'https://generativelanguage.googleapis.com/v1beta'
]

# Try all possible model names
MODELS_TO_TRY = [
    'gemini-1.5-pro-latest',
    'gemini-1.0-pro-latest',
    'gemini-pro',
    'models/gemini-1.5-pro-latest',
    'models/gemini-1.0-pro-latest',
    'models/gemini-pro'
]

# --- Connection Test ---
def test_connection():
    for endpoint in ENDPOINTS:
        try:
            response = requests.get(
                f"{endpoint}/models",
                headers={"x-goog-api-key": API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                return endpoint
        except:
            continue
    return None

working_endpoint = test_connection()

if not working_endpoint:
    st.error("🔥 Couldn't connect to any API endpoint. Check:")
    st.markdown("""
    - Your internet connection
    - API key validity
    - Google Cloud status page
    """)
    st.stop()

# --- Model Initialization ---
genai.configure(
    api_key=API_KEY,
    transport='rest',
    client_options={'api_endpoint': working_endpoint}
)

model = None
for model_name in MODELS_TO_TRY:
    try:
        model = genai.GenerativeModel(model_name)
        # Test the model
        test_response = model.generate_content("Test", request_options={"timeout": 5})
        if test_response.text:
            break
    except:
        continue

if not model:
    st.error("💥 No working model found. Available models:")
    try:
        st.write([m.name for m in genai.list_models()])
    except:
        st.write("Couldn't retrieve model list")
    st.stop()

# --- Streamlit UI ---
st.header("👨‍⚕️ Healthcare Advisor")
input_text = st.text_input("💊 Ask your health question")
submit = st.button("Get Answer")

# BMI Calculator
with st.sidebar:
    st.subheader("BMI Calculator")
    try:
        weight = float(st.text_input("Weight (kg)"))
        height = float(st.text_input("Height (cm)"))
        
        if weight and height:
            bmi = weight / ((height/100) ** 2)
            st.write(f"BMI: {bmi:.1f}")
            
            if bmi < 18.5:
                st.warning("Underweight")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight")
            elif 25 <= bmi < 30:
                st.warning("Overweight")
            else:
                st.error("Obese")
    except:
        st.warning("Enter valid numbers")

# Response Generation
if submit and input_text:
    try:
        with st.spinner("Generating response..."):
            response = model.generate_content(
                input_text,
                generation_config={"temperature": 0.7},
                request_options={"timeout": 10}
            )
            st.subheader("Response:")
            st.write(response.text)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.button("Try Again")

# Disclaimer
st.divider()
st.markdown("""
⚠️ **Disclaimer:**  
This is not medical advice. Always consult a doctor.
""")
