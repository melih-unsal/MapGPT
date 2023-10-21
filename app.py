import os
import pandas as pd
import streamlit as st
from src.models import ModelManager

title = "MapGPT"

st.set_page_config(page_title=title)
    
st.title(title)

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)

openai_api_base = st.sidebar.text_input(
    "Open AI base URL",
    placeholder="https://api.openai.com/v1",
)

models = (
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
)

model_name = st.sidebar.selectbox("Model", models)


with st.form("mapgpt", clear_on_submit=True):
    source_file = st.file_uploader("Choose Source CSV")
    target_file = st.file_uploader("Choose Target CSV")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        if not openai_api_key:
            st.warning("Please enter your OpenAI API Key!", icon="⚠️")
            st.stop()
        if not source_file:
            st.warning("Please upload the source file", icon="⚠️")
            st.stop()
        if not target_file:
            st.warning("Please upload the target file", icon="⚠️")
            st.stop()
            
        source = pd.read_csv(source_file, index_col=False)
        target = pd.read_csv(target_file, index_col=False)
        
        agent = ModelManager(source, 
                             target,    
                             model_name, 
                             openai_api_key, 
                             openai_api_base)
        
        with st.spinner("Running..."):
            results =  agent.run()
            confirmation = next(results)
            st.info(confirmation)      
            table = next(results)
            st.dataframe(table)
        
        
    