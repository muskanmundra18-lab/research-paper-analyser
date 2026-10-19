from rag import pdf_loader, chunkify, EmbeddingManager, VectorStoreManager, RAGRetriever, generate_output
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import hashlib
import json

load_dotenv()
api_key = os.getenv("Groq_API_KEY")

llm = ChatGroq(
    api_key=api_key,
    model="openai/gpt-oss-120b",
    max_tokens=1024,
    temperature=0.1
)


def get_pdf_fingerprint(folder_path="data/pdf"):
    """Generate a fingerprint for all PDFs in the folder."""

    hasher = hashlib.sha256()

    if not os.path.exists(folder_path):
        return None

    pdf_files = sorted(
        filename
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(".pdf")
    )

    if not pdf_files:
        return None

    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)

        hasher.update(filename.encode("utf-8"))

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

    return hasher.hexdigest()

embedding_manager = EmbeddingManager()
vector_store_manager = VectorStoreManager()


def index_pdfs():
    """Ingest and index PDFs only when necessary."""

    fingerprint = get_pdf_fingerprint()

    if fingerprint is None:
        return "No PDFs found. Please upload a PDF."

    metadata_path = "data/vector_store/index_metadata.json"

    os.makedirs("data/vector_store", exist_ok=True)

    # Check whether these exact PDFs are already indexed.
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if (
            metadata.get("fingerprint") == fingerprint
            and vector_store_manager.collection.count() > 0
        ):
            print("PDFs already indexed. Reusing vector store.")
            return "Documents already indexed."

    print("New or modified PDFs detected. Starting ingestion...")

    # Remove the previous collection.
    vector_store_manager.client.delete_collection(
        name=vector_store_manager.collection_name
    )

    # Create a fresh collection.
    vector_store_manager.collection = (
        vector_store_manager.client.create_collection(
            name=vector_store_manager.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    )

    documents = pdf_loader()

    if not documents:
        return "No readable PDF content found."

    chunked_docs = chunkify(documents)

    if not chunked_docs:
        return "No text extracted from PDFs."

    texts = [doc.page_content for doc in chunked_docs]

    embeddings = embedding_manager.generate_embeddings(texts)

    vector_store_manager.add_to_store(
        chunked_docs,
        embeddings
    )

    # Save the fingerprint only after successful indexing.
    with open(metadata_path, "w") as f:
        json.dump({"fingerprint": fingerprint}, f)

    print("Indexing completed.")
    print("Chunks indexed:", len(chunked_docs))

    return "Documents indexed successfully."


def final_output(query, top_k=5):
    if not query.strip():
        return "Please enter a question."

    if vector_store_manager.collection.count() == 0:
        return "No documents indexed. Please upload PDFs first."

    rag_retriever = RAGRetriever(
        embedding_manager,
        vector_store_manager
    )

    answer = generate_output(
        query,
        rag_retriever,
        llm,
        top_k=top_k
    )

    return answer


#Emptying Database
def clear_vector_store():
    persist_directory = "data/vector_store"
    collection_name = "pdf_documents"

    client = chromadb.PersistentClient(
        path=persist_directory
    )

    try:
        client.delete_collection(name=collection_name)
        print("Old ChromaDB collection deleted.")
    except Exception:
        print("No existing collection to delete.")

    print("Vector store cleared.")

def clear_pdf_folder():
    folder_path = "data/pdf"

    os.makedirs(folder_path, exist_ok=True)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(".pdf") and os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted old PDF: {filename}")

    print("PDF folder cleared.")