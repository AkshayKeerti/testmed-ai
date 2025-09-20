"""
FastAPI Backend for TrustMed AI
Main application entry point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import json
from typing import List, Dict, Any

from src.llm.llm_client import TrustMedLLMClient
from src.rag.rag_pipeline import TrustMedRAGPipeline
from src.api.models import ChatMessage, ChatResponse, HealthResponse
from src.api.auth import AuthManager
from src.api.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
llm_client = None
rag_pipeline = None
auth_manager = None
websocket_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global llm_client, rag_pipeline, auth_manager, websocket_manager
    
    # Startup
    logger.info("Starting TrustMed AI Backend...")
    llm_client = TrustMedLLMClient()
    rag_pipeline = TrustMedRAGPipeline()
    auth_manager = AuthManager()
    websocket_manager = WebSocketManager()
    
    logger.info("Backend startup complete!")
    yield
    
    # Shutdown
    logger.info("Shutting down TrustMed AI Backend...")

# Create FastAPI app
app = FastAPI(
    title="TrustMed AI API",
    description="Conversational AI for Medical Information",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="TrustMed AI Backend is running",
        llm_status=llm_client.test_connection() if llm_client else False
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """REST API chat endpoint with RAG"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
        
        # Generate response using RAG
        rag_response = rag_pipeline.generate_response(message.content)
        
        return ChatResponse(
            message=rag_response["answer"],
            sources=rag_response["sources"],
            confidence=rag_response["confidence"],
            timestamp=message.timestamp
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "")
                
                # Generate response using RAG
                rag_response = rag_pipeline.generate_response(user_message)
                
                # Send response
                await websocket_manager.send_message(websocket, {
                    "type": "response",
                    "message": rag_response["answer"],
                    "sources": rag_response["sources"],
                    "confidence": rag_response["confidence"]
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.send_error(websocket, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
