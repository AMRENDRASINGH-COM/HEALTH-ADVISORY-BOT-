import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Absolute Working Configuration (July 2024) ---
load_dotenv()
API_KEY = os.getenv("GOOGLE-API-KEY")

if not API_KEY:
    st.error("Please add GOOGLE_API_KEY to your .env file")
    st.stop()

# Configure with working endpoint
genai.configure(
    api_key=API_KEY,
    transport='rest',
    client_options={'api_endpoint': 'https://generativelanguage.googleapis.com/v1'}
)

# Use current working model (July 2024)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Streamlit UI ---
st.header("👨‍⚕️ Healthcare Advisor")

# BMI Calculator
with st.sidebar:
    st.subheader("BMI Calculator")
    weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=0.0, value=170.0, step=0.1)
    
    if weight and height:
        bmi = weight / ((height/100) ** 2)
        st.metric("Your BMI", f"{bmi:.1f}")

# Health Advisor
input_text = st.text_input("💊 Ask your health question", 
                          value="Give me a diet plan according to my BMI" if 'bmi' in locals() else "")

if st.button("Get Expert Advice"):
    if not input_text:
        st.warning("Please enter a question")
    else:
        try:
            with st.spinner("Generating expert advice..."):
                response = model.generate_content(
                    f"Act as a nutritionist. {input_text}. Current BMI: {bmi if 'bmi' in locals() else 'not provided'}",
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2000
                    },
                    safety_settings={
                        'HARM_CATEGORY_MEDICAL': 'BLOCK_NONE',
                        'HARM_CATEGORY_DANGEROUS': 'BLOCK_NONE'
                    }
                )
                st.subheader("Expert Recommendation:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            st.info("Please try again in a moment")

st.divider()
st.caption("⚠️ Disclaimer: This is not medical advice. Always consult a doctor.")
