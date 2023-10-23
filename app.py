import os
import pandas as pd
import streamlit as st
from time import sleep
from src.models import ModelManager

title = "MapGPT"

st.set_page_config(page_title=title, layout="wide")
    
st.title(title)

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)

openai_api_base = st.sidebar.text_input(
    "Open AI base URL (Optional)",
    placeholder="https://api.openai.com/v1",
)

models = (
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
)

model_name = st.sidebar.selectbox("Model", models)   

main_process, tables = st.columns(2)

with main_process:
    with st.form("mapgpt"):
        source_file = st.file_uploader("Choose Source CSV")
        target_file = st.file_uploader("Choose Target CSV")
        
        submitted = st.form_submit_button(label='Submit')
        
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
                
            st.session_state.source = pd.read_csv(source_file, index_col=False)
            st.session_state.target = pd.read_csv(target_file, index_col=False)
            
            st.session_state.agent = ModelManager(model_name, 
                                                openai_api_key, 
                                                openai_api_base,
                                                source=st.session_state.source,
                                                target=st.session_state.target)
            
            st.session_state.stage = 0
            
with tables:
    if st.session_state.get("source") is not None:
        st.subheader("Source")
        st.dataframe(st.session_state.source.head())
        
    if st.session_state.get("target") is not None:
        st.subheader("Target")
        st.dataframe(st.session_state.target.head())      

if st.session_state.get("source") is not None and st.session_state.get("target") is not None and st.session_state.get("stage",-1) != -1:
    if st.session_state.get("stage") == 0:
        st.session_state.agent.setTables(st.session_state.source, st.session_state.target)
        with st.spinner("Mapping Columns..."):
            st.session_state.confirmation =  st.session_state.agent.getConfirmationMessage()  
            st.session_state.stage = 1
    if st.session_state.get("confirmation"):
        st.json(st.session_state.confirmation)
        if st.session_state.stage == 3:
            st.info("Hi, again me. According to your feedback, i updated the mapping. Is it okay now")
        else:
            st.info("Hi, I'm MapGPT. According to the source and target tables, i created the following mapping. Is it okay for you?") 
        col1, col2 = st.columns(2)
        with col1:
            yes = st.button("Yes")
        with col2:
            no = st.button("No") 

else:
    yes = no = False  
        
if yes:
    progress_text = "Table is being reformatted..."
    progress_bar = st.progress(0, text=progress_text)
    data = None
    for data, percentage in st.session_state.agent.getTable():
        progress_bar.progress(percentage, text=progress_text)
    st.session_state.table = data 
    st.session_state.stage = -1
    st.rerun()
if no:
    print("no pressed")
    st.session_state.stage = 2


if st.session_state.get("stage") == 2:
    feedback = st.text_area("Give feedback")
    if st.button("Refine"):
        with st.spinner("Refining the mapping..."):
            st.session_state.confirmation = st.session_state.agent.refine(feedback)    
            st.session_state.stage = 3
            st.rerun()

if st.session_state.get("stage") == -1 and st.session_state.get("table") is not None:   
    st.subheader("Final Table") 
    st.dataframe(st.session_state.table)
    st.download_button(
        label="Download Table",
        data=st.session_state.table.to_csv().encode('utf-8'),
        file_name='final_table.csv',
        mime='text/csv'
        )

