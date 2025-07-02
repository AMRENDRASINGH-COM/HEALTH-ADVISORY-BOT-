import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()  # This will load the local environment vars...

# Set up the Gemini API key is VSCode
genai.configure(api_key = os.getenv("GOOGLE-API-KEY"))

# Streamlit Page
st.header("👨‍⚕️Healthcare :blue[Advisor]⚕️")
input = st.text_input("💊Hi! I am you Medical Expert. Ask me Anything")
submit = st.button("Submit")

# Create a BMI calculator -sidebar
st.sidebar.subheader("BMI Calculator")
weight = st.sidebar.text_input("Weight(in kgs):") # capture info in text
height = st.sidebar.text_input("height(in cms:)")

# BMI = weight/height**2
height_nums = pd.to_numeric(height)
weight_nums = pd.to_numeric(weight)
height_mts = height_nums/100
bmi = weight_nums/(height_mts)**2

# BMI Scale
notes = f'''The BMI value can be interpreted as:
* Underweight: BMI<18.5
* Normal Weight: BMI 18.5-24.9
* Overweight: BMI 25-29.9
* Obese: BMI>=30'''

if bmi:
    st.sidebar.markdown("The BMI is: ")
    st.sidebar.write(bmi)
    st.sidebat.write(notes)

# Generative AI application

def get_response(text):
    model = genai.GenerativeModel("gemini-pro")
    if text!= "":
        response = model.generate_content(text)
        return(response.text) 
    else:
        st.write("Please enter prompt!!")
    

if submit:
    response = get_response(input)
    st.subheader("The orange[Response] is: ")
    st.write(response)               

# Disclaimer
st.subheader("Disclaimer: ", divider=True)
notes = f'''
1. This is an advisor which is providing guidance and should not be construced as Medical Advice
2. Before taking any action, it is recommended to consult a Doctor.'''
st.markdown(notes)
