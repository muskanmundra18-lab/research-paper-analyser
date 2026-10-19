#Import Modules
import os
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import uuid
from dotenv import load_dotenv
from langchain_groq import ChatGroq

#Ingestion Pipeline 

def pdf_loader():
    folder_path = "data/pdf"
    num_docs = 0
    all_docs = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path,filename)

            loader = PyPDFLoader(pdf_path)
            doc = loader.load()
            all_docs.extend(doc)
            num_docs+=1
    print(f"no. of docs = {num_docs}")
    print(f"no. of pages = {len(all_docs)}")
    return all_docs

def chunkify(document, chunk_size = 500, chunk_overlap = 50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunked_docs = text_splitter.split_documents(document)
    return chunked_docs

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        print("loading model...", self.model_name)
        self.model = SentenceTransformer(self.model_name)
        print("embedding dimensions = ", self.model.get_sentence_embedding_dimension())

    def generate_embeddings(self, text):
        embeddings = self.model.encode(text, show_progress_bar=True)
        print(embeddings.shape)
        return embeddings


class VectorStoreManager:
    def __init__(self, persist_directory="data/vector_store", collection_name="pdf_documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_directory)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description":"vector store collection for pdf embedding for RAG"}
        )

        print("Initialised the vector store for pdf documents")
        print("collection count=", self.collection.count())

    def add_to_store(self, documents, embeddings):
        if len(documents)!= len(embeddings):
            raise ValueError("length of document and embeddings doesn't match")

        ids = []
        all_metadata = []
        document_content = []
        embeddings_list = []

        for i,(doc,embedding) in enumerate(zip(documents,embeddings)):

            ids.append(f"doc_{uuid.uuid4()}")
            metadata = dict(doc.metadata)
            metadata["doc_index"] = i
            metadata["content_length"] = len(doc.page_content)

            all_metadata.append(metadata)

            document_content.append(doc.page_content)

            embeddings_list.append(embedding.tolist())

            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=all_metadata,
                documents=document_content
            )

        print("total documents added in the vector store:", len(document_content))
        print("docs in collection:", self.collection.count())

#Retrieval Pipeline 

class RAGRetriever :
    def __init__(self, embedding_manager, vector_store):
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedding_manager.generate_embeddings(query[0])

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results = top_k
        )

        retrieved_docs = []
        if results["documents"] and results["documents"][0]:
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            documents = results["documents"][0]

            for i, (id,metadata,distance,document) in enumerate(zip(ids,metadatas,distances,documents)):

                retrieved_docs.append({
                    "id":id,
                    "metadata":metadata,
                    "document":document,
                    "distance":distance,
                    "rank":i+1        
                })

            print(f"retrieved {len(retrieved_docs)} documents")
            
        else:
            print("no documents found")
            
        return retrieved_docs

#Generation Pipeline

load_dotenv()
api_key = os.getenv("Groq_API_KEY")

llm = ChatGroq(
    api_key=api_key,
    model="openai/gpt-oss-120b",
    max_tokens=1024,
    temperature=0.1
)

def generate_output(query, retriever, llm, top_k=5):
    results = retriever.retrieve(query,top_k)
    context = "\n".join([doc["document"] for doc in results]) if results else ""

    if not context:
        print("We couldn't find relevent response to the query")

    prompt = f"""Use the given context to generate the answer for the query
                    context:{context}
                    query:{query}"""
    response = llm.invoke([prompt.format(context=context, query=query)])
    return response.content

