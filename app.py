import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Attractive Header Section ---
st.set_page_config(page_title="HealthGenie AI", page_icon="🧞", layout="wide")

# Main header with emoji and styling
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🧞 HealthGenie AI ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Your 24/7 Personal Health Companion 🩺 | Nutrition Guide 🥗 | Fitness Coach 💪</div>', unsafe_allow_html=True)

# Animated divider
st.markdown("---")
st.markdown("🌟 **Ask me anything about health, nutrition, or fitness!** 🌟")

# Sidebar - BMI Calculator with attractive design
with st.sidebar:
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-header">📊 BMI Calculator</div>', unsafe_allow_html=True)
    
    # BMI Calculator content remains the same as before
    weight = st.text_input("Weight (in kg):", key="weight")
    height = st.text_input("Height (in cm):", key="height")
    
    if st.button("Calculate BMI 🧮", key="bmi_button"):
        try:
            weight_num = float(weight)
            height_num = float(height)
            if height_num <= 0 or weight_num <= 0:
                st.error("Please enter valid positive numbers")
            else:
                height_m = height_num / 100
                bmi = weight_num / (height_m ** 2)
                st.balloons()
                st.success(f"Your BMI: {bmi:.2f}")
                
                # BMI Interpretation with emojis
                if bmi < 18.5:
                    st.warning("Underweight: BMI < 18.5 🏋️‍♂️ Eat more nutritious foods!")
                elif 18.5 <= bmi < 25:
                    st.success("Normal weight: BMI = 18.5-24.9 ✅ Great job!")
                elif 25 <= bmi < 30:
                    st.warning("Overweight: BMI = 25-29.9 🚶‍♂️ Consider more exercise")
                else:
                    st.error("Obese: BMI ≥ 30 ⚠️ Please consult a doctor")
        except ValueError:
            st.error("Please enter valid numbers")

# Main Content - Healthcare Advisor with attractive design
st.markdown("""
<style>
    .question-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    input_prompt = st.text_area("💬 **Hi! I'm Dr. Genie, your AI health expert. Ask me anything about:**\n\n• Nutrition 🥑\n• Exercise 🏃‍♀️\n• Symptoms 🤒\n• Mental Health 🧠\n• General Wellness 🌿", 
                              key="input", 
                              height=150)
    st.markdown('</div>', unsafe_allow_html=True)

    submit = st.button("✨ Get Expert Advice", type="primary")

def get_gemini_response(question):
    try:
        model = genai.GenerativeModel("gemini-1.0-pro")
        if question.strip() != "":
            with st.spinner("🧞 Dr. Genie is thinking..."):
                response = model.generate_content(question)
                return response.text
        else:
            return "Please enter a valid health question."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if submit:
    if input_prompt:
        response = get_gemini_response(input_prompt)
        st.markdown("---")
        st.subheader("🧪 **Dr. Genie's Advice:**", divider="rainbow")
        st.markdown(f"""
        <div style="
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4b8bbe;
        ">
            {response}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter your health question first")

# Enhanced Disclaimer
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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 14px;">
    Made with ❤️ by HealthGenie AI | © 2023 All Rights Reserved
</div>
""", unsafe_allow_html=True)
