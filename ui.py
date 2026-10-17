import os
import streamlit as st
from rag import final_output
SAVE_DIR = "data/pdf"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.title("Scientific Research Paper Analyser")
st.write("Upload your Research Paper PDF here...")

uploaded_files = st.file_uploader(
    "Choose PDF file(s)", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(SAVE_DIR, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())


query = st.text_input(
    label="What do you want to ask?", 
    placeholder="Enter your query..."
)

button = st.button("Answer...")

def get_output(query):
    answer = final_output(query)
    return answer


if uploaded_files and button:
    answer = get_output(query)
    st.write(answer)