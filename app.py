import os
import streamlit as st
from rag import final_output, clear_pdf_folder, clear_vector_store
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
    label="Ask about your research paper", 
    placeholder="Enter your query..."
)

button = st.button("Answer")


if uploaded_files and button:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analysing your research papers..."):
            try:
                result = final_output(query)

                st.subheader("Answer")
                st.write(result)

            except Exception as e:
                st.error(f"An error occurred: {e}")

new_chat = st.button("New Chat")

if new_chat:
    clear_vector_store()
    clear_pdf_folder()
