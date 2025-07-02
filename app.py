import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import time
from datetime import datetime

# --- Environment Setup with Enhanced Error Handling ---
try:
    load_dotenv('.env')
    API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")
    if not API_KEY:
        st.error("🔑 API key not found. Please check your .env file")
        st.markdown("""
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 10px; border-left: 5px solid #ffa000;">
            <p>Ensure your <code>.env</code> file contains:</p>
            <code>GOOGLE_API_KEY=your_actual_api_key_here</code>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
except Exception as e:
    st.error(f"Configuration error: {str(e)}")
    st.stop()

# --- Robust API Initialization ---
def initialize_generative_model():
    """Comprehensive initialization with multiple fallback strategies"""
    endpoints = [
        ('v1', 'https://generativelanguage.googleapis.com/v1'),
        ('v1beta', 'https://generativelanguage.googleapis.com/v1beta')
    ]
    
    model_priority = [
        'models/gemini-1.5-pro-latest',
        'models/gemini-1.0-pro-latest',
        'models/gemini-pro',
        'gemini-pro'  # Legacy format
    ]
    
    for version, endpoint in endpoints:
        try:
            # First verify endpoint accessibility
            response = requests.get(
                f"{endpoint}/models",
                headers={"x-goog-api-key": API_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    genai.configure(
                        api_key=API_KEY,
                        transport='rest',
                        client_options={'api_endpoint': endpoint}
                    )
                    
                    for model_name in model_priority:
                        try:
                            model = genai.GenerativeModel(model_name)
                            # Verify with test prompt
                            test_response = model.generate_content(
                                "Connection test",
                                request_options={"timeout": 10}
                            )
                            if test_response.text:
                                return model, model_name, version
                        except Exception:
                            continue
                except Exception as e:
                    continue
        except requests.exceptions.RequestException:
            continue
    
    # If all attempts fail
    raise ConnectionError("Could not establish connection with any API endpoint or model")

# --- Initialize Model with Comprehensive Error Reporting ---
if 'genai_model' not in st.session_state:
    try:
        model, model_name, api_version = initialize_generative_model()
        st.session_state.genai_model = model
        st.session_state.model_name = model_name
        st.session_state.api_version = api_version
    except Exception as e:
        st.error(f"🚨 Initialization failed: {str(e)}")
        st.markdown("""
        <div style="background-color: #ffebee; padding: 15px; border-radius: 10px; border-left: 5px solid #f44336;">
            <h4>🔧 Troubleshooting Steps:</h4>
            <ol>
                <li>Verify your <strong>API key is valid</strong> at <a href="https://makersuite.google.com/app/apikey" target="_blank">Google MakerSuite</a></li>
                <li>Check <strong>API status</strong> at <a href="https://status.cloud.google.com/" target="_blank">Google Cloud Status</a></li>
                <li>Ensure <strong>billing is enabled</strong> in <a href="https://console.cloud.google.com/billing" target="_blank">Google Cloud Console</a></li>
                <li>Confirm <strong>Generative Language API is enabled</strong> in <a href="https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com" target="_blank">Google Cloud Console</a></li>
                <li>Try again in 5-10 minutes (temporary issues may resolve)</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# --- UI Configuration ---
st.set_page_config(
    page_title="HealthGenie AI",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        margin-top: -2rem;
        padding-top: 0;
    }
    .header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4b8bbe;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .tagline {
        font-size: 1.1rem;
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        background-color: #4b8bbe;
        padding: 0.75rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .question-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        background-color: #4b8bbe;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3a7ba8;
        transform: translateY(-1px);
    }
    footer {visibility: hidden;}
    .response-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4b8bbe;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)
st.markdown("---")

# --- BMI Calculator ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 BMI Calculator</div>', unsafe_allow_html=True)
    weight = st.number_input("Weight (kg):", min_value=0.0, value=70.0, step=0.1)
    height = st.number_input("Height (cm):", min_value=0.0, value=170.0, step=0.1)
    
    if st.button("Calculate BMI 🧮"):
        if height > 0 and weight > 0:
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            st.balloons()
            
            if bmi < 18.5:
                st.warning(f"BMI: {bmi:.1f} - Underweight 🏋️‍♂️ Eat more nutritious foods!")
            elif 18.5 <= bmi < 25:
                st.success(f"BMI: {bmi:.1f} - Normal weight ✅ Great job!")
            elif 25 <= bmi < 30:
                st.warning(f"BMI: {bmi:.1f} - Overweight 🚶‍♂️ Consider more exercise")
            else:
                st.error(f"BMI: {bmi:.1f} - Obese ⚠️ Please consult a doctor")
        else:
            st.error("Please enter valid positive numbers")
    
    # Connection info
    with st.expander("🔧 Connection Status"):
        if 'model_name' in st.session_state:
            st.success(f"Connected to: {st.session_state.model_name}")
            st.success(f"API Version: {st.session_state.api_version}")
        if st.button("Refresh Connection"):
            st.session_state.pop('genai_model', None)
            st.rerun()

# --- Health Advisor ---
with st.container():
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    input_prompt = st.text_area(
        "💬 **Hi! I'm Dr. Genie, your AI health expert. Ask me anything about:**\n\n"
        "• Nutrition 🥑\n• Exercise 🏃‍♀️\n• Symptoms 🤒\n• Mental Health 🧠\n• General Wellness 🌿", 
        height=150
    )
    st.markdown('</div>', unsafe_allow_html=True)

    submit = st.button("✨ Get Expert Advice", type="primary")

# --- Response Generation with Comprehensive Error Handling ---
if submit and input_prompt:
    try:
        with st.spinner("🧞 Dr. Genie is analyzing your question..."):
            response = st.session_state.genai_model.generate_content(
                f"Act as a professional dietitian and health expert. {input_prompt}",
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
                st.markdown("---")
                st.subheader("🧪 Dr. Genie's Advice:", divider="rainbow")
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #4b8bbe;">
                    {response.text}
                    <p style="text-align: right; color: #6c757d; font-size: 0.8rem;">
                        Powered by {st.session_state.model_name}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Received empty response from the AI model")
    except Exception as e:
        st.error(f"Failed to generate response: {str(e)}")
        st.info("Please try again or rephrase your question")
        
# --- Disclaimer ---
st.markdown("---")
with st.expander("📝 Important Medical Disclaimer"):
    st.markdown("""
    <div style="color: #6c757d;">
        <p>⚠️ <strong>This AI provides general health information only</strong> 🏥</p>
        <p>• Not a substitute for professional medical advice 👨‍⚕️</p>
        <p>• Always consult a qualified healthcare provider 🩺</p>
        <p>• Information accuracy not guaranteed 📊</p>
        <p>• Use at your own discretion 🤝</p>
        <p><em>Your health and safety are our top priority</em> ❤️</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem; padding-top: 2rem;">
    Made with ❤️ by HealthGenie AI | © {datetime.now().year} All Rights Reserved
</div>
""", unsafe_allow_html=True)
