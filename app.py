import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import time

# --- Environment Setup ---
load_dotenv('.env')  # For local testing; Streamlit Cloud uses secrets

# --- API Configuration ---
api_key = st.secrets.get("GOOGLE-API-KEY")
if not api_key:
    st.error("API key not found. Please check your Streamlit secrets")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Explicitly use supported model
except Exception as e:
    st.error(f"API setup error: {str(e)}")
    st.stop()

# --- UI Header ---
st.set_page_config(page_title="HealthGenie AI", page_icon="🩺", layout="wide")
st.markdown("""
<style>
    .header { font-size: 50px !important; font-weight: bold; color: #4b8bbe; 
              text-align: center; padding: 20px; background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
              border-radius: 15px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); margin-bottom: 25px; }
    .tagline { font-size: 20px !important; text-align: center; color: #6c757d; margin-bottom: 30px; }
    .sidebar-header { font-size: 25px !important; font-weight: bold; color: #ffffff; 
                     background-color: #4b8bbe; padding: 10px; border-radius: 10px; 
                     text-align: center; margin-bottom: 20px; }
    .input-header { font-size: 22px; font-weight: bold; color: #2c6e49; 
                   text-align: center; padding: 10px; background-color: #e8f5e9; 
                   border-radius: 10px; margin-bottom: 10px; }
    .advice-box { background-color: #fff3e6; padding: 20px; border-radius: 15px; 
                 border-left: 6px solid #ff7043; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                 font-size: 16px; line-height: 1.6; color: #333; }
    .advice-title { color: #ff7043; font-size: 24px; font-weight: bold; margin-bottom: 10px; 
                   text-align: center; text-transform: uppercase; }
    .divider-rainbow { border: none; border-top: 4px dashed #ff7043; margin: 20px 0; }
    .stTextArea textarea { margin-top: 0 !important; padding: 10px; }
    .stTextArea { margin-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🩺 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Session State for BMI ---
if 'bmi' not in st.session_state:
    st.session_state.bmi = None

# --- BMI Calculator ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 BMI Calculator</div>', unsafe_allow_html=True)
    weight = st.number_input("Weight (in kg):", min_value=0.0, format="%.1f", key="weight")
    height = st.number_input("Height (in cm):", min_value=0.0, format="%.1f", key="height")
    
    if st.button("Calculate BMI 🧮", key="bmi_button"):
        if height > 0 and weight > 0:
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            st.session_state.bmi = bmi
            st.balloons()
            st.success(f"Your BMI: {bmi:.2f}")
            if bmi < 18.5:
                st.warning("Underweight: BMI < 18.5 🏋‍♂ Eat more nutritious foods!")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight: BMI = 18.5-24.9 ✅ Great job!")
            elif 25 <= bmi < 30:
                st.warning("Overweight: BMI = 25-29.9 🚶‍♂ Consider more exercise")
            else:
                st.error("Obese: BMI ≥ 30 ⚠ Please consult a doctor")
        else:
            st.error("Please enter valid positive numbers")

# --- Health Advisor ---
with st.container():
    st.markdown('<div class="input-header">🌿 Ask Dr. Genie Your Health Questions</div>', unsafe_allow_html=True)
    input_prompt = st.text_area("", key="input", height=150, placeholder="💬 Ask about Nutrition, Exercise, Symptoms, Mental Health, or Wellness...")
    submit = st.button("✨ Get Expert Advice", type="primary")

# --- Response Generation ---
if submit:
    if input_prompt:
        try:
            with st.spinner("🧞 Dr. Genie is thinking..."):
                # Include BMI in the prompt if available
                bmi_context = f"Your BMI is {st.session_state.bmi:.2f}." if st.session_state.bmi else "No BMI data available. Please calculate your BMI first."
                full_prompt = f"Act as a professional dietitian and health expert. {bmi_context} {input_prompt}"
                response = model.generate_content(
                    full_prompt,
                    generation_config={"temperature": 0.7}
                )
                if response.text:
                    st.markdown("---")
                    st.markdown('<div class="divider-rainbow"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="advice-title">Dr. Genie\'s Advice</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="advice-box">{response.text}</div>', unsafe_allow_html=True)
                else:
                    st.error("No response from the model.")
        except Exception as e:
            st.error(f"Response failed: {str(e)}")
    else:
        st.warning("⚠ Please enter your health question first")

# --- Disclaimer ---
st.markdown("---")
with st.expander("📝 Important Disclaimer"):
    st.markdown("""
    ⚠ *Please Note:*  
    - This AI provides general health information only 🏥  
    - Not a substitute for professional medical advice 👨‍⚕  
    - Always consult a real doctor for serious conditions 🩺  
    - Results may not be 100% accurate 📊  
    - Use at your own discretion 🤝  
    Your health is important to us! ❤  
    """)

st.markdown("---")
st.markdown("""<div style="text-align: center; color: #6c757d; font-size: 14px;">
    Made with ❤ by HealthGenie AI | © 2023 All Rights Reserved</div>""", 
    unsafe_allow_html=True)
