import streamlit as st 
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import time
from google.api_core import exceptions

# --- Improved Environment Setup ---
# Explicitly load .env from current directory
load_dotenv('.env')  # Added explicit path

# Debugging - verify environment variables
st.session_state.debug = False  # Set to True for debugging
if st.session_state.debug:
    st.write("Environment variables:", os.environ)

# --- API Configuration with Error Handling ---
try:
    # Match the exact key name in your .env file
    api_key = os.getenv("GOOGLE-API-KEY")  # Now matches your .env exactly
    
    if not api_key:
        st.error("API key not found in environment variables")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    # Verify API connection
    try:
        available_models = genai.list_models()
        if st.session_state.debug:
            st.write("Available models:", [m.name for m in available_models])
    except Exception as e:
        st.error(f"API connection failed: {str(e)}")
        st.stop()
        
except Exception as e:
    st.error(f"Configuration error: {str(e)}")
    st.stop()

# --- Improved Gemini Response Function ---
def get_gemini_response(question):
    try:
        model = genai.GenerativeModel("gemini-1.0-pro")
        
        if not question.strip():
            return "Please enter a valid health question."
        
        with st.spinner("🧞 Dr. Genie is thinking..."):
            start_time = time.time()
            
            # Added timeout and better response handling
            response = model.generate_content(
                question,
                request_options={"timeout": 30}  # 30 second timeout
            )
            
            # Check for empty response
            if not response.text:
                raise ValueError("Empty response from API")
                
            return response.text
            
    except exceptions.DeadlineExceeded:
        return "Request timed out. Please try again."
    except exceptions.InvalidArgument as e:
        return f"Invalid request: {str(e)}"
    except exceptions.PermissionDenied:
        return "API key rejected. Please check your credentials."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# --- Rest of your UI code remains the same ---
[Keep all your existing UI code exactly as is, including headers, BMI calculator, etc.]

# --- Modified Submit Section ---
if submit:
    if input_prompt:
        response = get_gemini_response(input_prompt)
        st.markdown("---")
        st.subheader("🧪 **Dr. Genie's Advice:**", divider="rainbow")
        
        # Improved response display with error handling
        if response.startswith(("Request timed out", "Invalid request", "API key rejected", "An error occurred")):
            st.error(response)
        else:
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

[Keep the rest of your existing code]
