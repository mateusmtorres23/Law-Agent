import fitz
import os
import pymupdf4llm
from sentence_transformers import SentenceTransformer
from agno.agent import Agent
from agno.models.ollama import Ollama

os.environ["HF_HUB_OFFLINE"] = "1"

embedder = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v1.5", 
    device="cpu", 
    trust_remote_code=True,
    model_kwargs={"local_files_only": True}
)

def process_pdf_bytes(file_bytes: bytes) -> list[dict]:
    doc = fitz.open("pdf", file_bytes)
    markdown_content = pymupdf4llm.to_markdown(doc)
    
    chunk_size = 1000
    overlap = 200
    chunks = []
    
    start = 0
    text_length = len(markdown_content)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = markdown_content[start:end]
        chunks.append(chunk_text)
        start += (chunk_size - overlap)
    
    processed_chunks = []
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        vector = embedder.encode(chunk).tolist()
        processed_chunks.append({
            "content": chunk,
            "embedding": vector
        })
        
    return processed_chunks

def embed_query(query: str) -> list[float]:
    return embedder.encode(query).tolist()

def generate_response(user_message: str, retrieved_context: list[str]) -> str:
    law_agent = Agent(
        model=Ollama(id="qwen3.5:2b"),
        description="A specialized legal assistant focused on case analysis.",
        instructions=["Base your answers strictly on the provided context.", "Be formal and precise.",
                      """If the question is about a broad theme, check if there's some correlation with the retrieved context 
                      and answer based on that. If not, answer based on general legal knowledge."""],
    )
    
    context_str = "\n\n---\n\n".join(retrieved_context) if retrieved_context else "No context found."
    prompt = f"Context:\n{context_str}\n\nQuestion: {user_message}"
    
    response = law_agent.run(prompt)
    return str(response.content) if response.content else "Error: No response generated."