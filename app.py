import os
import pandas as pd
import streamlit as st
from time import sleep
from src.models import ModelManager

title = "🔄 MapGPT"

st.set_page_config(page_title=title, layout="wide")
    
st.title(title)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = st.secrets.get("LANGCHAIN_API_KEY","")
os.environ["LANGCHAIN_PROJECT"] = st.secrets.get("LANGCHAIN_PROJECT","")

_ = """openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)

openai_api_base = st.sidebar.text_input(
    "Open AI base URL (Optional)",
    placeholder="https://api.openai.com/v1",
)"""

openai_api_key = st.secrets.get("OPENAI_API_KEY",os.getenv("OPENAI_API_KEY",""))
openai_api_base = st.secrets.get("OPENAI_API_BASE",os.getenv("OPENAI_API_BASE",""))

models = (
    "gpt-3.5-turbo-1106",
    "finetuned_model",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-1106-preview"
)

model_name = st.sidebar.selectbox("Model", models)   

main_process, tables = st.columns(2)

with main_process:
    with st.form("mapgpt"):
        source_file = st.file_uploader("Choose Source CSV/Excel", type=["csv","xlsx"])
        target_file = st.file_uploader("Choose Target CSV/Excel", type=["csv","xlsx"])
        
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
            if source_file.name.endswith(".csv"):
                st.session_state.source = pd.read_csv(source_file, index_col=False)
            else:
                st.session_state.source = pd.read_excel(source_file, index_col=False)
            
            if target_file.name.endswith(".csv"):
                st.session_state.target = pd.read_csv(target_file, index_col=False)
            else:
                st.session_state.target = pd.read_excel(target_file, index_col=False)
            
            if 'Unnamed: 0' in st.session_state.source.columns:
                st.session_state.source = st.session_state.source.drop(columns='Unnamed: 0')
            
            if 'Unnamed: 0' in st.session_state.target.columns:
                st.session_state.target = st.session_state.target.drop(columns='Unnamed: 0')
            
            st.session_state.agent = ModelManager(model_name, 
                                                openai_api_key, 
                                                openai_api_base,
                                                source=st.session_state.source,
                                                target=st.session_state.target)
            
            st.session_state.stage = 0
            
with tables:
    if st.session_state.get("source") is not None:
        st.subheader("Source")
        st.dataframe(st.session_state.source)
        
    if st.session_state.get("target") is not None:
        st.subheader("Target")
        st.dataframe(st.session_state.target)      

if st.session_state.get("source") is not None and st.session_state.get("target") is not None and st.session_state.get("stage",-1) != -1 and model_name != "finetuned_model":
    if st.session_state.get("stage") == 0:
        st.session_state.agent.setTables(st.session_state.source, st.session_state.target)
        with st.spinner("Mapping Columns..."):
            st.session_state.confirmation =  st.session_state.agent.getConfirmationMessage()  
            st.session_state.stage = 1
    if st.session_state.get("confirmation"):
        previous = st.session_state.confirmation["previous"]
        after = st.session_state.confirmation["after"]
        st.subheader("Original Row")
        st.dataframe(previous)
        st.subheader("✏️Transformed Row")
        st.info("If any cells require edits, please click on them and make the necessary changes.")
        st.session_state.edited_row = st.data_editor(after)
        st.info("""Greetings from MapGPT. Based on the provided source and target tables, I've made adjustments to the initial row. Please take a moment to review the table. If you wish to make corrections, simply click on any cell to modify its contents. Once you're satisfied with the updates, kindly click the 'Submit' button to finalize your changes. If no corrections are required, you may proceed by pressing 'Submit' directly.""") 

if st.session_state.get("source") is not None and st.session_state.get("target") is not None and st.session_state.get("stage",-1) != -1 and model_name == "finetuned_model":
    with st.spinner('Table is being created...'):
        progress_text = "Final Table is being prepared..."
        progress_bar = st.progress(0, text=progress_text)
        data = None
        for data, percentage in st.session_state.agent.getTableWithFinetunedModel():
            progress_bar.progress(percentage, text=progress_text)
        st.session_state.table = data 
        st.session_state.stage = -1
        #st.rerun()

if st.session_state.get("stage") == 1 and model_name != "finetuned_model":
    finalize_table = st.button("Submit")
        
    if finalize_table:
        with st.spinner('Table is being finalized...'):
            progress_text = "Final Table is being prepared..."
            progress_bar = st.progress(0, text=progress_text)
            data = None
            for data, percentage in st.session_state.agent.getTable(st.session_state.edited_row):
                progress_bar.progress(percentage, text=progress_text)
            st.session_state.table = data 
            st.session_state.stage = -1
            st.rerun()

if st.session_state.get("stage") == -1 and st.session_state.get("table") is not None:   
    st.subheader("Final Table") 
    # st.dataframe(st.session_state.table)
    final_table = st.data_editor(st.session_state.table)
    st.download_button(
        label="Download Table",
        data=final_table.to_csv().encode('utf-8'),
        file_name='final_table.csv',
        mime='text/csv'
        )

