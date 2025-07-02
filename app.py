import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from datetime import datetime

# --- Environment Setup ---
load_dotenv()  # Load environment variables from .env file

# Configure Gemini API
try:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE-API-KEY")
    if not api_key:
        st.error("API key not found. Please check your .env file")
        st.stop()
    
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Failed to configure API: {str(e)}")
    st.stop()

# Initialize the model with error handling
try:
    # Try multiple model names with fallback
    try:
        model = genai.GenerativeModel('gemini-pro')
    except:
        model = genai.GenerativeModel('models/gemini-pro')
except Exception as e:
    st.error(f"Failed to initialize model: {str(e)}")
    st.markdown("""
    <div style="background-color: #ffebee; padding: 15px; border-radius: 10px;">
        <h4>Troubleshooting:</h4>
        <ol>
            <li>Verify your API key is correct</li>
            <li>Check <a href="https://status.cloud.google.com/">Google Cloud Status</a></li>
            <li>Ensure billing is enabled in Google Cloud Console</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- UI Configuration ---
st.set_page_config(
    page_title="HealthGenie AI",
    page_icon="🧞",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4b8bbe;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }
    .question-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

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
