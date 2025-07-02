import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import time
import traceback
from datetime import datetime

# --- Environment Setup with Error Handling ---
try:
    load_dotenv('.env')
except Exception as e:
    st.error(f"Failed to load environment variables: {str(e)}")
    st.stop()

# --- API Configuration with Multiple Fallbacks ---
def initialize_generative_model():
    """Robust initialization with multiple fallback strategies"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")

    if not api_key:
        raise ValueError("🔑 API key not found. Please check your .env file or Streamlit secrets")

    # Test API endpoints directly
    endpoints = [
        ('v1', 'https://generativelanguage.googleapis.com/v1'),
        ('v1beta', 'https://generativelanguage.googleapis.com/v1beta')
    ]
    
    for version, endpoint in endpoints:
        try:
            response = requests.get(
                f"{endpoint}/models",
                headers={"x-goog-api-key": api_key},
                timeout=15
            )
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                st.session_state.available_models = models
                
                # Configure the working endpoint
                genai.configure(
                    api_key=api_key,
                    transport='rest',
                    client_options={'api_endpoint': endpoint}
                )
                
                # Try model variants in priority order
                model_variants = [
                    'gemini-1.5-pro-latest',
                    'gemini-1.0-pro-latest',
                    'gemini-pro',
                    'models/gemini-1.0-pro',
                    'models/gemini-pro'
                ]
                
                for model_name in model_variants:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Test with a simple prompt
                        test_response = model.generate_content(
                            "Connection test",
                            request_options={"timeout": 10}
                        )
                        if test_response.text:
                            return model, model_name, version
                    except Exception:
                        continue
                
        except requests.exceptions.RequestException:
            continue
    
    # If all attempts fail
    available = st.session_state.get('available_models', [])
    raise ConnectionError(
        f"🔌 Could not connect to any Gemini API endpoint.\n"
        f"Available models: {available if available else 'None found'}"
    )

# --- UI Configuration with Custom CSS ---
st.set_page_config(
    page_title="HealthGenie AI",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Remove white space and improve layout */
    .stApp {
        margin-top: -2rem;
        padding: 0;
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

# --- App Initialization with Error Recovery ---
if 'genai_model' not in st.session_state:
    try:
        model, model_name, api_version = initialize_generative_model()
        st.session_state.genai_model = model
        st.session_state.model_name = model_name
        st.session_state.api_version = api_version
        
        # Log successful connection
        print(f"Successfully connected to {model_name} (API {api_version})")
        
    except Exception as e:
        st.error(f"🚨 Initialization Error: {str(e)}")
        if 'available_models' in st.session_state:
            st.error(f"🔍 Available models: {st.session_state.available_models}")
        
        st.markdown("""
        <div class="error-box">
            <h4>🚑 Troubleshooting Guide:</h4>
            <ol>
                <li>Verify your <code>GOOGLE_API_KEY</code> in <code>.env</code> or Streamlit secrets</li>
                <li>Check API status at <a href="https://status.cloud.google.com/">Google Cloud Status</a></li>
                <li>Ensure "Generative Language API" is enabled in <a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
                <li>Try again in 5 minutes (temporary issues may resolve)</li>
                <li>Contact support if problem persists</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

# --- Header Section ---
st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)
st.markdown("---")

# --- BMI Calculator ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 BMI Calculator</div>', unsafe_allow_html=True)
    
    try:
        weight = st.number_input("Weight (kg):", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
        height = st.number_input("Height (cm):", min_value=0.0, max_value=250.0, value=170.0, step=0.1)
        
        if st.button("Calculate BMI 🧮"):
            if height > 0 and weight > 0:
                height_m = height / 100
                bmi = weight / (height_m ** 2)
                
                st.balloons()
                bmi_status = ""
                if bmi < 18.5:
                    bmi_status = "Underweight 🏋️‍♂️ Eat more nutritious foods!"
                elif 18.5 <= bmi < 25:
                    bmi_status = "Normal weight ✅ Great job!"
                elif 25 <= bmi < 30:
                    bmi_status = "Overweight 🚶‍♂️ Consider more exercise"
                else:
                    bmi_status = "Obese ⚠️ Please consult a doctor"
                
                st.success(f"Your BMI: {bmi:.1f} - {bmi_status}")
            else:
                st.error("Please enter valid positive numbers")
                
    except Exception as e:
        st.error(f"BMI calculation error: {str(e)}")

# --- Health Advisor ---
try:
    with st.container():
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        input_prompt = st.text_area(
            "💬 **Hi! I'm Dr. Genie, your AI health expert. Ask me anything about:**\n\n"
            "• Nutrition 🥑\n• Exercise 🏃‍♀️\n• Symptoms 🤒\n• Mental Health 🧠\n• General Wellness 🌿",
            height=150
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submit = st.button("✨ Get Expert Advice", type="primary")

    if submit and input_prompt:
        try:
            with st.spinner("🧞 Dr. Genie is analyzing your question..."):
                start_time = time.time()
                
                response = st.session_state.genai_model.generate_content(
                    f"""As a professional health expert, provide detailed, evidence-based advice for:
                    
                    {input_prompt}
                    
                    Include:
                    - Practical recommendations
                    - Scientific rationale
                    - Safety considerations
                    - When to consult a doctor""",
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_output_tokens": 2000
                    },
                    safety_settings={
                        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                    },
                    stream=False,
                    request_options={"timeout": 20}
                )
                
                processing_time = time.time() - start_time
                
                if response.text:
                    st.markdown("---")
                    st.subheader("🧪 **Dr. Genie's Expert Advice**", divider="rainbow")
                    st.markdown(f"""
                    <div class="response-box">
                        {response.text}
                        <p style="text-align: right; color: #6c757d; font-size: 0.8rem;">
                            Generated in {processing_time:.2f}s using {st.session_state.model_name}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Received empty response from the AI model")
                    
        except Exception as e:
            st.error(f"🚨 Response generation failed: {str(e)}")
            st.markdown(f"""
            <div class="error-box">
                <p>We couldn't generate a response. Please:</p>
                <ul>
                    <li>Try rephrasing your question</li>
                    <li>Check your internet connection</li>
                    <li>Wait a moment and try again</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
    elif submit:
        st.warning("⚠️ Please enter your health question first")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.stop()

# --- Disclaimer ---
st.markdown("---")
with st.expander("📝 Important Medical Disclaimer"):
    st.markdown("""
    <div style="color: #6c757d;">
        <p>⚠️ <strong>This AI provides general health information only</strong> 🏥</p>
        <p>• Not a substitute for professional medical advice 👨‍⚕️</p>
        <p>• Always consult a qualified healthcare provider for serious conditions 🩺</p>
        <p>• Information accuracy not guaranteed 📊</p>
        <p>• Use at your own discretion 🤝</p>
        <p><em>Your health and safety are our top priority</em> ❤️</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem; padding-top: 2rem;">
    Made with ❤️ by HealthGenie AI | © {year} All Rights Reserved
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)
