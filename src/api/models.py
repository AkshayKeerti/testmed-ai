"""
Pydantic models for TrustMed AI API
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Chat message model"""
    content: str
    timestamp: datetime = datetime.now()
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    sources: List[Dict[str, Any]] = []
    confidence: float
    timestamp: datetime = datetime.now()

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    llm_status: bool

class User(BaseModel):
    """User model"""
    id: str
    email: str
    name: str
    created_at: datetime = datetime.now()

class AuthRequest(BaseModel):
    """Authentication request model"""
    email: str
    password: str

class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str
    token_type: str = "bearer"
    user: User
