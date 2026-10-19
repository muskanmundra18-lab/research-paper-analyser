import os
import streamlit as st

from backend import index_pdfs, final_output, clear_pdf_folder, clear_vector_store

SAVE_DIR = "data/pdf"

os.makedirs(SAVE_DIR, exist_ok=True)

st.title("Scientific Research Paper Analyser")

st.write("Upload your research papers and ask questions about them.")

uploaded_files = st.file_uploader(
    "Choose PDF file(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    # Identify the uploaded batch by file names and contents.
    import hashlib

    uploaded_signature = []

    for file in uploaded_files:
        file_hash = hashlib.sha256(file.getvalue()).hexdigest()

        uploaded_signature.append(
            (file.name, file_hash)
        )

    uploaded_signature = tuple(sorted(uploaded_signature))

    # Only save and index if the uploaded batch changes.
    if st.session_state.get("uploaded_signature") != uploaded_signature:

        with st.spinner("Preparing research papers..."):

            # Remove previous PDFs.
            for filename in os.listdir(SAVE_DIR):
                file_path = os.path.join(SAVE_DIR, filename)

                if (
                    filename.lower().endswith(".pdf")
                    and os.path.isfile(file_path)
                ):
                    os.remove(file_path)

            # Save the new PDFs.
            for uploaded_file in uploaded_files:
                file_path = os.path.join(
                    SAVE_DIR,
                    uploaded_file.name
                )

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Index the new batch.
            status = index_pdfs()

            st.session_state.uploaded_signature = uploaded_signature

            st.success(status)

query = st.text_input(
    "What do you want to ask?",
    placeholder="Enter your query..."
)

if st.button("Answer..."):
    if not query.strip():
        st.warning("Please enter a question.")

    elif not os.listdir(SAVE_DIR):
        st.warning("Please upload a research paper first.")

    else:
        with st.spinner("Finding relevant information..."):
            answer = final_output(query)

        st.subheader("Answer")
        st.write(answer)

new_chat = st.button("New Chat")

if new_chat:
    clear_vector_store()
    clear_pdf_folder()