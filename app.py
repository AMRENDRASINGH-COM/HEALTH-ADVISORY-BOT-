import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv() # This will load the environment variables from the .env file
import langchain
import pandas as pd
# Set up the gemini API key in VScode
genai.configure(api_key= os.getenv("GOOGLE-API-KEY"))
# Stremlit Page
st.header("Healthcare :blue[Advisor] ",divider="green")
input = st.text_input("Hi! I am your medical Expert. Ask me any question about your health")
submit = st.button("Submit")

# create the BMI calculater - sidebar
st.sidebar.header("BMI Calculator")
weight = st.sidebar.text_input("Weight (in kgs):") # Capture info in text
height = st.sidebar.text_input("Height (in cms):")
# Create a button to calculate BMI
# BMI = weight/height**2
height_num = pd.to_numeric(height)
weight_num = pd.to_numeric(weight)
height_mts = height_num/100
bmi = weight_num/(height_mts)**2
st.sidebar.markdown(bmi)

# BMI Scale
notes = f''' The BMI value can be determined as follows:
* Underweight: BMI < 18.5
* Normal weight: BMI = 18.5-24.9
* Overweight: BMI = 25-29.9
* Obese: BMI ≥ 30'''
if bmi:
    st.sidebar.markdown('The BMI is')
    st.sidebar.write(bmi)
    st.sidebar.write(notes)

# Generative AI application
def get_response(text):
    model = genai.GenerativeModel("gemini-pro")
    if text!="":
        response = model.generate_content(text)
        return(response.text)
    else:
        st.write("Please enter a Promt!!")
    

if submit:
    response = get_response(input)
    st.subheader("The :violet[Response] is:")
    st.write(response)

# Disclaimer
st.subheader("Disclaimer:",divider=True)
notes = f'''
1. This is a simple application and not a substitute for professional medical advice.
2. Before taking any action, it is recommended to consult a doctor.'''
st.markdown(notes)
