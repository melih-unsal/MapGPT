import streamlit as st
import pandas as pd

st.download_button(
    label="Download data as CSV",
    data=pd.read_csv("data/table_A.csv").to_csv().encode('utf-8'),
    file_name='large_df.csv',
    mime='text/csv',
)