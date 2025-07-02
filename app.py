import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# --- Environment Setup ---
load_dotenv('.env')

# --- API Configuration with Comprehensive Error Handling ---
def initialize_generative_model():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")

    if not api_key:
        raise ValueError("API key not found. Please check your .env file or Streamlit secrets")

    try:
        # Configure with multiple endpoint options
        endpoints_to_try = [
            'https://generativelanguage.googleapis.com/v1beta',
            'https://generativelanguage.googleapis.com/v1'
        ]
        
        for endpoint in endpoints_to_try:
            try:
                genai.configure(
                    api_key=api_key,
                    transport='rest',
                    client_options={'api_endpoint': endpoint}
                )
                
                # Get available models for debugging
                available_models = [m.name for m in genai.list_models()]
                if not available_models:
                    continue
                
                # Try all possible model naming patterns
                model_names_to_try = [
                    'gemini-1.5-pro-latest',
                    'gemini-1.0-pro-latest',
                    'gemini-pro',
                    'models/gemini-1.0-pro',
                    'models/gemini-pro'
                ]
                
                for model_name in model_names_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        # Verify with test prompt
                        model.generate_content("Connection test", request_options={"timeout": 5})
                        return model, model_name, endpoint, available_models
                    except Exception:
                        continue
                        
            except Exception:
                continue
                
        raise ConnectionError("Failed to establish connection with any API endpoint or model")

    except Exception as e:
        raise RuntimeError(f"API configuration failed: {str(e)}")

# --- UI Setup ---
st.set_page_config(
    page_title="HealthGenie AI",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        margin-top: -75px;
        padding-top: 0px;
    }
    .header { 
        font-size: 50px !important; 
        font-weight: bold; 
        color: #4b8bbe; 
        text-align: center; 
        padding: 20px; 
        background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px; 
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); 
        margin-bottom: 25px; 
    }
    .tagline { 
        font-size: 20px !important; 
        text-align: center; 
        color: #6c757d; 
        margin-bottom: 30px; 
    }
    .sidebar-header { 
        font-size: 25px !important; 
        font-weight: bold; 
        color: #ffffff; 
        background-color: #4b8bbe; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .question-box { 
        background-color: #f8f9fa; 
        border-radius: 10px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1); 
    }
    footer {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Model with Error Handling ---
if 'genai_model' not in st.session_state:
    try:
        model, active_model, active_endpoint, available_models = initialize_generative_model()
        st.session_state.genai_model = model
        st.session_state.active_model = active_model
        st.session_state.active_endpoint = active_endpoint
        st.session_state.available_models = available_models
    except Exception as e:
        st.error(str(e))
        st.stop()

# --- Header Section ---
st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)
st.markdown("---")

# --- BMI Calculator (Sidebar) ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 BMI Calculator</div>', unsafe_allow_html=True)
    weight = st.number_input("Weight (in kg):", min_value=0.0, format="%.1f", key="weight")
    height = st.number_input("Height (in cm):", min_value=0.0, format="%.1f", key="height")
    
    if st.button("Calculate BMI 🧮", key="bmi_button"):
        if height > 0 and weight > 0:
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            st.balloons()
            st.success(f"Your BMI: {bmi:.2f}")
            
            if bmi < 18.5:
                st.warning("Underweight: BMI < 18.5 🏋️‍♂️ Eat more nutritious foods!")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight: BMI = 18.5-24.9 ✅ Great job!")
            elif 25 <= bmi < 30:
                st.warning("Overweight: BMI = 25-29.9 🚶‍♂️ Consider more exercise")
            else:
                st.error("Obese: BMI ≥ 30 ⚠️ Please consult a doctor")
        else:
            st.error("Please enter valid positive numbers")
    
    # Debug information
    with st.expander("🔧 Connection Details"):
        if 'active_model' in st.session_state:
            st.success(f"Active Model: {st.session_state.active_model}")
            st.success(f"API Endpoint: {st.session_state.active_endpoint}")
        if 'available_models' in st.session_state:
            st.write("Available models:", st.session_state.available_models)

# --- Health Advisor ---
with st.container():
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    input_prompt = st.text_area("💬 **Hi! I'm Dr. Genie, your AI health expert. Ask me anything about:**\n\n• Nutrition 🥑\n• Exercise 🏃‍♀️\n• Symptoms 🤒\n• Mental Health 🧠\n• General Wellness 🌿", 
                              key="input", height=150)
    st.markdown('</div>', unsafe_allow_html=True)

    submit = st.button("✨ Get Expert Advice", type="primary")

# --- Response Generation with Error Handling ---
if submit and input_prompt:
    try:
        with st.spinner("🧞 Dr. Genie is thinking..."):
            response = st.session_state.genai_model.generate_content(
                f"Act as a professional dietitian and health expert. {input_prompt}",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000
                },
                stream=False,
                request_options={"timeout": 10}
            )
            
            if response.text:
                st.markdown("---")
                st.subheader("🧪 **Dr. Genie's Advice:**", divider="rainbow")
                st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #4b8bbe;">
                    {response.text}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Received empty response from the AI model")
    except Exception as e:
        st.error(f"Failed to generate response: {str(e)}")
        st.info("Try refreshing the page or checking your internet connection")
elif submit:
    st.warning("⚠️ Please enter your health question first")

# --- Disclaimer ---
st.markdown("---")
with st.expander("📝 Important Disclaimer"):
    st.markdown("""
    ⚠️ **Please Note:**  
    - This AI provides general health information only 🏥  
    - Not a substitute for professional medical advice 👨‍⚕️  
    - Always consult a real doctor for serious conditions 🩺  
    - Results may not be 100% accurate 📊  
    - Use at your own discretion 🤝  
    *Your health is important to us!* ❤️  
    """)

# --- Footer ---
st.markdown("""<div style="text-align: center; color: #6c757d; font-size: 14px; padding-top: 20px;">
    Made with ❤️ by HealthGenie AI | © 2023 All Rights Reserved</div>""", 
    unsafe_allow_html=True)
