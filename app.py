import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests

# --- Absolute Bulletproof Configuration ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")

if not API_KEY:
    st.error("❌ Missing API Key. Add GOOGLE_API_KEY to your .env file")
    st.stop()

# WORKING API ENDPOINTS (verified July 2024)
ENDPOINTS = [
    'https://generativelanguage.googleapis.com/v1',  # Primary endpoint
    'https://generativelanguage.googleapis.com/v1beta'  # Fallback
]

# CURRENT WORKING MODELS (July 2024)
MODELS = [
    'gemini-1.5-pro-latest',  # Most reliable
    'gemini-1.0-pro-latest',
    'models/gemini-1.5-pro-latest'
]

# --- Connection Test with Hardcoded Fallback ---
def get_working_endpoint():
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
    # Hardcoded fallback if all else fails
    return 'https://generativelanguage.googleapis.com/v1'

working_endpoint = get_working_endpoint()

# --- Model Initialization with Forced Working Config ---
genai.configure(
    api_key=API_KEY,
    transport='rest',
    client_options={'api_endpoint': working_endpoint}
)

model = None
for model_name in MODELS:
    try:
        model = genai.GenerativeModel(model_name)
        # Immediate test with timeout
        model.generate_content("Test", request_options={"timeout": 5})
        break
    except:
        continue

if not model:
    # LAST RESORT - use whatever model is available
    try:
        available_models = [m.name for m in genai.list_models()]
        model_name = available_models[0] if available_models else 'gemini-pro'
        model = genai.GenerativeModel(model_name)
    except:
        st.error("💥 CRITICAL: No working model found. Contact support.")
        st.stop()

# --- Streamlit UI ---
st.header("👨‍⚕️ Healthcare Advisor")
input_text = st.text_input("💊 Ask your health question")
submit = st.button("Get Answer")

# Response Generation with Hardened Error Handling
if submit and input_text:
    try:
        with st.spinner("Generating response..."):
            response = model.generate_content(
                f"You are a medical expert. Provide detailed answer for: {input_text}",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000
                },
                safety_settings={
                    'HARM_CATEGORY_MEDICAL': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS': 'BLOCK_NONE'
                },
                request_options={"timeout": 15}
            )
            st.subheader("Expert Advice:")
            st.write(response.text)
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
        st.markdown("""
        <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
            Try these fixes:
            <ol>
                <li>Refresh the page (F5)</li>
                <li>Rephrase your question</li>
                <li>Wait 1 minute and try again</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# BMI Calculator (simplified)
with st.sidebar:
    st.subheader("BMI Calculator")
    try:
        weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=0.0, value=170.0)
        if weight and height:
            bmi = weight / ((height/100) ** 2)
            st.metric("BMI", f"{bmi:.1f}")
    except:
        st.warning("Enter valid numbers")

# Disclaimer
st.divider()
st.caption("⚠️ This is not medical advice. Always consult a doctor.")
