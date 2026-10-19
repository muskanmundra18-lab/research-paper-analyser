# Scientific Research Paper Analyser

An AI-powered research paper analysis tool that allows users to upload PDF documents and ask questions about their content using **Retrieval-Augmented Generation (RAG)**.

Built with Streamlit, LangChain, Sentence Transformers, ChromaDB, and Groq, the application retrieves relevant information from uploaded research papers and uses a large language model to generate context-aware answers.

## Overview

Reading and understanding lengthy research papers can be time-consuming. This project simplifies the process by allowing users to interact with research documents through natural-language questions.

Instead of relying entirely on an LLM's pretrained knowledge, the application retrieves relevant text from the uploaded documents and uses that context to generate responses.

## Features

* **PDF Upload:** Upload research papers and other PDF documents for analysis.
* **Document Processing:** Extract text from PDFs and divide it into smaller chunks for efficient retrieval.
* **Semantic Search:** Generate embeddings using Sentence Transformers to identify document passages relevant to a question.
* **Vector Database:** Store and retrieve document embeddings using ChromaDB.
* **Persistent Storage:** Preserve indexed document embeddings between application sessions.
* **Context-Aware Q&A:** Ask questions in natural language and receive answers generated using relevant document context.
* **LLM Integration:** Use Groq's inference API with the `openai/gpt-oss-120b` model for answer generation.
* **Interactive Interface:** Upload documents and interact with the system through a Streamlit web application.

## Tech Stack

| Component             | Technology                     |
| --------------------- | ------------------------------ |
| Programming Language  | Python                         |
| Frontend              | Streamlit                      |
| PDF Processing        | PyPDFLoader                    |
| Text Splitting        | RecursiveCharacterTextSplitter |
| Embedding Model       | `all-MiniLM-L6-v2`             |
| Vector Database       | ChromaDB                       |
| LLM Inference         | Groq API                       |
| LLM                   | `openai/gpt-oss-120b`          |
| Framework             | LangChain                      |
| Environment Variables | python-dotenv                  |

## How It Works

The application follows a Retrieval-Augmented Generation pipeline.

```text
             PDF Upload
                  |
                  v
          PDF Text Extraction
                  |
                  v
            Text Splitting
                  |
                  v
          Generate Embeddings
                  |
                  v
          Store in ChromaDB
                  |
                  v
        User Enters a Question
                  |
                  v
       Generate Query Embedding
                  |
                  v
       Retrieve Relevant Chunks
                  |
                  v
       Construct Context + Query
                  |
                  v
          Groq LLM Inference
                  |
                  v
          Generate Final Answer
```

### 1. Document Ingestion

Uploaded PDFs are processed using LangChain's `PyPDFLoader` to extract their textual content.

The extracted text is divided into smaller chunks using `RecursiveCharacterTextSplitter`, with the following configuration:

* **Chunk size:** 500 characters
* **Chunk overlap:** 50 characters

Chunking allows the application to retrieve focused sections of a research paper instead of processing the entire document for every question.

### 2. Embedding Generation

Each document chunk is converted into a numerical vector using the Sentence Transformers model:

`all-MiniLM-L6-v2`

These embeddings represent the semantic meaning of the text and allow the application to retrieve relevant passages based on meaning rather than exact keyword matches.

### 3. Vector Storage and Retrieval

The generated embeddings are stored in a persistent ChromaDB collection named `pdf_documents`.

When a user submits a question, the system searches the vector database for relevant document chunks.

This retrieval step supplies the LLM with information from the uploaded research papers.

### 4. Answer Generation

The retrieved document context and the user's question are passed to a Groq-hosted language model.

The model generates a response using the retrieved information, allowing users to explore the contents of their research papers interactively.

## Getting Started

Follow these steps to run the project locally.

### Prerequisites

* Python 3.10 or a compatible version supported by the dependencies
* Git
* A Groq API key

### 1. Clone the Repository

```bash
git clone https://github.com/muskanmundra18-lab/research-paper-analyser.git
```

Navigate to the project directory:

```bash
cd research-paper-analyser
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your Groq API key using the environment variable expected by your application.

```env
Groq_API_KEY=your_groq_api_key
```

Replace the placeholder with your actual API key.

You can obtain an API key through the official [Groq Console](https://console.groq.com/).

**Security note:** Never commit your `.env` file or expose your API key in your source code.

### 5. Run the Application

```bash
streamlit run app.py
```

Streamlit will provide a local URL where you can access the application.

## Usage

1. Start the Streamlit application.
2. Upload one or more research paper PDFs through the interface.
3. Allow the documents to be processed and indexed.
4. Enter a question about the uploaded research material.
5. Submit the question.
6. Review the generated answer.

### Example Questions

You can ask questions such as:

* What is the main objective of this research paper?
* Which methodology does the paper propose?
* What are the key findings?
* Which algorithms or models are used?
* What limitations do the authors identify?
* Explain the proposed approach in simple terms.
* What conclusions can be drawn from the research?

The answers depend on the quality of the extracted text, the retrieved document chunks, and the language model's interpretation of the supplied context.

## Project Structure

The following is an illustrative structure for the application. Adapt the filenames to match your repository.

```text
research-paper-analyser/
│
├── app.py                  # Streamlit application
├── rag.py                  # RAG pipeline and retrieval logic
├── backend.py              # Backend for the app
├── requirements.txt        # Python dependencies
├── .env                    # API credentials (not committed)
├── .gitignore
│
└── data/
    ├── pdf/                # Uploaded PDF documents
    └── vector_store/       # Persistent ChromaDB data
```

## Key Concepts Demonstrated

This project demonstrates practical implementation of several concepts in modern AI application development:

* Retrieval-Augmented Generation (RAG)
* Semantic search and vector embeddings
* Document ingestion and preprocessing
* Vector database integration
* Large Language Model (LLM) inference
* Prompt construction using retrieved context
* Persistent vector storage
* Building interactive AI applications with Streamlit
* Managing API credentials through environment variables

## Potential Improvements

Future enhancements could include:

* Displaying source documents and page references for generated answers.
* Supporting document-specific retrieval when multiple PDFs are uploaded.
* Improving retrieval with metadata filtering and reranking.
* Adding conversation history for follow-up questions.
* Supporting scanned PDFs through OCR.
* Evaluating retrieval quality and answer faithfulness.
* Adding automated tests for document ingestion and retrieval.

## Limitations

* Answer quality depends on the relevance of retrieved document chunks.
* Scanned PDFs may require OCR if they do not contain extractable text.
* An LLM may generate incorrect information if the retrieved context is insufficient or ambiguous.
* The application requires a valid Groq API key for model inference.
* Persistent vector storage requires appropriate handling when documents are replaced or deleted.

For research and academic work, verify important claims against the original paper rather than treating generated answers as authoritative.

## Author

**Muskan Mundra**

* GitHub: [@muskanmundra18-lab](https://github.com/muskanmundra18-lab)
* Project Repository: [Research Paper Analyser](https://github.com/muskanmundra18-lab/research-paper-analyser)

---

*Built to make exploring scientific research papers faster and more interactive using Retrieval-Augmented Generation.*
