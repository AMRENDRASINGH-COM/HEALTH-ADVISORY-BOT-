import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import time
from datetime import datetime

# --- Environment Setup ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")

if not API_KEY:
    st.error("❌ API key not found. Please check your .env file")
    st.stop()

# --- Robust Model Initialization ---
def get_working_model():
    endpoints = [
        'https://generativelanguage.googleapis.com/v1',
        'https://generativelanguage.googleapis.com/v1beta'
    ]
    
    model_priority = [
        'gemini-1.5-pro-latest',
        'gemini-1.0-pro-latest',
        'gemini-pro',
        'models/gemini-1.5-pro-latest',
        'models/gemini-1.0-pro-latest',
        'models/gemini-pro'
    ]
    
    for endpoint in endpoints:
        try:
            # Test endpoint first
            response = requests.get(
                f"{endpoint}/models",
                headers={"x-goog-api-key": API_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                genai.configure(
                    api_key=API_KEY,
                    transport='rest',
                    client_options={'api_endpoint': endpoint}
                )
                
                for model_name in model_priority:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Verify the model works
                        test_response = model.generate_content("Test", request_options={"timeout": 5})
                        if test_response.text:
                            return model, model_name, endpoint
                    except Exception:
                        continue
        except requests.exceptions.RequestException:
            continue
    
    # If we get here, all attempts failed
    try:
        available = [m.name for m in genai.list_models()]
        st.error(f"Available models: {available}")
    except:
        st.error("Could not retrieve available models")
    
    raise Exception("❌ Could not initialize any working model")

# --- Initialize Model ---
if 'model' not in st.session_state:
    try:
        model, model_name, endpoint = get_working_model()
        st.session_state.model = model
        st.session_state.model_info = f"{model_name} @ {endpoint}"
    except Exception as e:
        st.error(str(e))
        st.markdown("""
        <div style="background-color: #ffebee; padding: 15px; border-radius: 10px; border-left: 5px solid #f44336;">
            <h4>🚨 Required Fixes:</h4>
            <ol>
                <li>Verify API key at <a href="https://makersuite.google.com/app/apikey" target="_blank">MakerSuite</a></li>
                <li>Enable API at <a href="https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com" target="_blank">Google Cloud Console</a></li>
                <li>Check billing at <a href="https://console.cloud.google.com/billing" target="_blank">Billing Page</a></li>
                <li>Wait 5 minutes if you just enabled the API</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# --- UI Setup --- [Keep your existing UI code]
st.set_page_config(page_title="HealthGenie AI", page_icon="🧞", layout="wide")


# --- Modified Response Generation ---
if submit and input_prompt:
    try:
        with st.spinner("🧞 Generating expert advice..."):
            response = st.session_state.model.generate_content(
                f"Act as a medical expert. Provide detailed advice for: {input_prompt}",
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
            
            if response.text:
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #4b8bbe;">
                    {response.text}
                    <p style="text-align: right; color: #6c757d; font-size: 0.8rem;">
                        Generated using {st.session_state.model_info.split('@')[0].strip()}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Received empty response")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.button("🔄 Try Again", key="retry_button")

# --- App UI ---
st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)

# BMI Calculator
with st.sidebar:
    st.title("📊 BMI Calculator")
    weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, value=170.0)
    if st.button("Calculate BMI"):
        if height > 0 and weight > 0:
            bmi = weight / ((height/100) ** 2)
            st.success(f"BMI: {bmi:.1f}")

# Main Chat Interface
with st.container():
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    prompt = st.text_area("Ask your health question:")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Get Expert Advice"):
        if prompt:
            try:
                with st.spinner("Generating response..."):
                    response = model.generate_content(
                        f"As a medical expert, answer: {prompt}",
                        generation_config={
                            "temperature": 0.7,
                            "max_output_tokens": 2000
                        }
                    )
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px;">
                        {response.text}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
        else:
            st.warning("Please enter a question")

# Footer
st.markdown(f"""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    HealthGenie AI © {datetime.now().year}
</div>
""", unsafe_allow_html=True)
