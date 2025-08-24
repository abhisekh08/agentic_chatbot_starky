import streamlit as st

credentials = {'APP_NAME': st.secrets["APP"]['APP_NAME'],
               'GROQ_API_KEY': st.secrets['API']['GROQ_API_KEY'],
               'TAVILY_API_KEY':st.secrets["API"]['TAVILY_API_KEY'],
               'MODEL_NAME':st.secrets["MODEL"]['MODEL_NAME']
               }