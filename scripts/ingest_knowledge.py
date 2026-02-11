import os
import sys
import glob
import chromadb
from pypdf import PdfReader

# Add src to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.llm_client import LLMClient

# Configuration
KNOWLEDGE_DIR = "knowledge"
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "design_patterns"

def ingest_pdfs():
    # Initialize LLM Client for embeddings
    print("Initializing LLM Client...")
    llm_client = LLMClient()

    # Initialize ChromaDB
    print(f"Initializing ChromaDB at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # We will manually compute embeddings using LLMClient, so we don't pass an embedding_function here
    # content is stored as 'documents', embeddings as 'embeddings'
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    pdf_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {KNOWLEDGE_DIR}")
        return

    print(f"Found {len(pdf_files)} PDFs. Starting ingestion...")

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for file_path in pdf_files:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")
        
        try:
            reader = PdfReader(file_path)
            full_text = ""
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
            
            chunk_size = 1000
            overlap = 100
            
            text_len = len(full_text)
            start = 0
            chunk_idx = 0
            
            while start < text_len:
                end = start + chunk_size
                chunk = full_text[start:end]
                
                documents.append(chunk)
                metadatas.append({"source": filename, "chunk": chunk_idx})
                ids.append(f"{filename}_{chunk_idx}")
                
                # Generate embedding using LLMClient
                # Method defined as get_embedding(text: str) -> list[float]
                emb = llm_client.get_embedding(chunk)
                embeddings.append(emb)

                start += (chunk_size - overlap)
                chunk_idx += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if documents:
        print(f"Upserting {len(documents)} chunks to ChromaDB...")
        collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print("Ingestion complete.")
    else:
        print("No text extracted from PDFs.")

if __name__ == "__main__":
    ingest_pdfs()
