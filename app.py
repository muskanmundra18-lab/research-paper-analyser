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
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analysing your research papers..."):
            try:
                result = final_output(query)

                st.subheader("Answer")
                st.write(result["answer"])

                with st.expander("Inspect retrieved context"):
                    if result["sources"]:
                        for i, doc in enumerate(result["sources"]):
                            st.markdown(f"### Retrieved chunk {i + 1}")

                            st.write(
                                "Source:",
                                doc["metadata"].get("source", "Unknown")
                            )

                            st.write(
                                "Page:",
                                doc["metadata"].get("page", "Unknown")
                            )

                            st.write(
                                "Similarity:",
                                round(doc["similarity_score"], 4)
                            )

                            st.write(doc["document"])
                            st.divider()
                    else:
                        st.warning("No context was retrieved.")

            except Exception as e:
                st.error(f"An error occurred: {e}")