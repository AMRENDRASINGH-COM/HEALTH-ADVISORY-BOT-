import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import time
from datetime import datetime

# --- Environment Setup ---
try:
    load_dotenv('.env')
    API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")
    if not API_KEY:
        st.error("API key not found. Please check your .env file")
        st.stop()
except Exception as e:
    st.error(f"Configuration error: {str(e)}")
    st.stop()

# --- Model Initialization with Fallbacks ---
def initialize_model():
    """Robust model initialization with multiple fallbacks"""
    endpoints = [
        'https://generativelanguage.googleapis.com/v1',
        'https://generativelanguage.googleapis.com/v1beta'
    ]
    
    model_priority = [
        'models/gemini-1.5-pro-latest',  # Most recent stable
        'models/gemini-1.5-pro-002',
        'models/gemini-1.5-pro',
        'models/gemini-2.5-pro',         # Newest version
        'models/gemini-2.5-flash',
        'models/gemini-1.0-pro-latest'   # Fallback
    ]
    
    for endpoint in endpoints:
        try:
            genai.configure(
                api_key=API_KEY,
                transport='rest',
                client_options={'api_endpoint': endpoint}
            )
            
            for model_name in model_priority:
                try:
                    model = genai.GenerativeModel(model_name)
                    # Test connection with simple prompt
                    response = model.generate_content(
                        "Connection test",
                        request_options={"timeout": 10}
                    )
                    if response.text:
                        return model, model_name, endpoint
                except Exception:
                    continue
                    
        except Exception:
            continue
    
    # If all attempts fail
    try:
        available_models = [m.name for m in genai.list_models()]
        st.error(f"Available models: {available_models}")
    except:
        st.error("Could not retrieve available models")
    
    raise ConnectionError("Failed to initialize any model. See available models above.")

# --- Initialize Model ---
if 'model' not in st.session_state:
    try:
        model, model_name, endpoint = initialize_model()
        st.session_state.model = model
        st.session_state.model_name = model_name
        st.session_state.endpoint = endpoint
    except Exception as e:
        st.error(f"Initialization failed: {str(e)}")
        st.error("""
        Troubleshooting:
        1. Verify API key is correct
        2. Check https://status.cloud.google.com/
        3. Ensure billing is enabled
        4. Try a different model name
        """)
        st.stop()

# --- UI Configuration ---
st.set_page_config(
    page_title="HealthGenie AI",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as previous)
# ... [include your CSS here] ...

# --- App UI ---
st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion</div>', unsafe_allow_html=True)

# BMI Calculator
with st.sidebar:
    st.markdown("### 📊 BMI Calculator")
    weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, value=170.0)
    if st.button("Calculate BMI"):
        if height > 0 and weight > 0:
            bmi = weight / ((height/100) ** 2)
            st.success(f"BMI: {bmi:.1f}")

# Main Chat Interface
prompt = st.text_area("Ask your health question:")
if st.button("Get Expert Advice"):
    if prompt:
        try:
            with st.spinner("Generating response..."):
                response = st.session_state.model.generate_content(
                    f"As a medical expert, answer: {prompt}",
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2000
                    },
                    safety_settings={
                        'HARM_CATEGORY_MEDICAL': 'BLOCK_NONE',
                        'HARM_CATEGORY_DANGEROUS': 'BLOCK_NONE'
                    }
                )
                st.markdown(f"""
                <div class="response-box">
                    {response.text}
                    <p style="color: #666; font-size: 0.8rem;">
                        Generated using {st.session_state.model_name}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question")

# Model Info in Sidebar
with st.sidebar.expander("⚙️ Connection Info"):
    st.write(f"**Active Model:** {st.session_state.model_name}")
    st.write(f"**API Endpoint:** {st.session_state.endpoint}")
    if st.button("Refresh Connection"):
        st.session_state.pop('model', None)
        st.rerun()

# Disclaimer
with st.expander("⚠️ Important Disclaimer"):
    st.markdown("""
    This is an AI assistant, not a medical professional. 
    Always consult a doctor for medical advice.
    """)

st.markdown(f"""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    HealthGenie AI © {datetime.now().year}
</div>
""", unsafe_allow_html=True)
