import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.database import init_db, get_db_connection, insert_case, get_cases, insert_message
from app.api.agent import process_pdf_bytes, embed_query, generate_response

app = FastAPI(title="Law Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/api/cases")
def create_case(title: str):
    now = datetime.now().isoformat()
    return insert_case(title, now)

@app.get("/api/cases")
def list_cases():
    return get_cases()

@app.post("/api/cases/{case_id}/documents")
async def upload_document(case_id: int, file: UploadFile = File(...)):
    if file.filename is None or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="A valid PDF file is required.")
    
    file_bytes = await file.read()
    chunks = process_pdf_bytes(file_bytes)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (case_id, filename, text_content) VALUES (?, ?, ?)", 
            (case_id, file.filename, "Binary parsed in memory.")
        )
        doc_id = cursor.lastrowid
        
        for chunk in chunks:
            cursor.execute(
                "INSERT INTO document_chunks (document_id, case_id, text_content, embedding) VALUES (?, ?, ?, ?)",
                (doc_id, case_id, chunk["content"], str(chunk["embedding"]))
            )
        conn.commit()
        
    return {"status": "success", "chunks_ingested": len(chunks)}

@app.websocket("/api/chat/{case_id}")
async def chat_endpoint(websocket: WebSocket, case_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_text = message_data.get("text", "")
            
            insert_message(case_id, "user", user_text)
            query_vector = embed_query(user_text)
            
            with get_db_connection() as conn:
                rows = conn.execute("""
                    SELECT text_content 
                    FROM document_chunks 
                    WHERE case_id = ? AND embedding MATCH ? AND k = 3
                    ORDER BY distance
                """, (case_id, str(query_vector))).fetchall()
                
                retrieved_context = [row["text_content"] for row in rows]
            
            response_text = generate_response(user_text, retrieved_context)
            insert_message(case_id, "ai", response_text)
            
            await websocket.send_json({
                "role": "ai",
                "content": response_text
            })
            
    except WebSocketDisconnect:
        pass