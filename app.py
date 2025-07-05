import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import time

# --- Environment Setup ---
load_dotenv('.env')  # Optional for local testing; Streamlit Cloud uses secrets

# --- API Configuration ---
api_key = st.secrets.get("GOOGLE-API-KEY")  # Use Streamlit secrets
if not api_key:
    st.error("API key not found. Please check your Streamlit secrets")
    st.stop()

try:
    genai.configure(api_key=api_key)
    # Explicitly try using gemini-pro
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"API configuration failed: {str(e)}")
    st.stop()

# --- UI Header ---
st.set_page_config(page_title="HealthGenie AI", page_icon="🧞", layout="wide")
st.markdown("""
<style>
    .header { font-size: 50px !important; font-weight: bold; color: #4b8bbe; 
              text-align: center; padding: 20px; background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
              border-radius: 15px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); margin-bottom: 25px; }
    .tagline { font-size: 20px !important; text-align: center; color: #6c757d; margin-bottom: 30px; }
    .sidebar-header { font-size: 25px !important; font-weight: bold; color: #ffffff; 
                     background-color: #4b8bbe; padding: 10px; border-radius: 10px; 
                     text-align: center; margin-bottom: 20px; }
    .question-box { background-color: #f8f9fa; border-radius: 10px; padding: 20px; 
                   margin-bottom: 20px; box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)
st.markdown("---")

# --- BMI Calculator ---
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
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    input_prompt = st.text_area("💬 *Hi! I'm Dr. Genie, your AI health expert. Ask me anything about:*\n\n• Nutrition 🥑\n• Exercise 🏃‍♀\n• Symptoms 🤒\n• Mental Health 🧠\n• General Wellness 🌿", 
                              key="input", height=150)
    st.markdown('</div>', unsafe_allow_html=True)

    submit = st.button("✨ Get Expert Advice", type="primary")

# --- Response Generation ---
if submit:
    if input_prompt:
        try:
            with st.spinner("🧞 Dr. Genie is thinking..."):
                response = model.generate_content(
                    f"Act as a professional dietitian and health expert. {input_prompt}",
                    generation_config={"temperature": 0.7}
                )
                
                if response.text:
                    st.markdown("---")
                    st.subheader("🧪 *Dr. Genie's Advice:*", divider="rainbow")
                    st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #4b8bbe;">
                        {response.text}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Received empty response from the AI model")
        except Exception as e:
            st.error(f"Failed to generate response: {str(e)}")
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
