from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AgentRequest(BaseModel):
    query: str
    image: Optional[str] = None
    video: Optional[str] = None

class AgentResponse(BaseModel):
    claims: List[Dict[str, Any]]
    verdict: str               # One of: Supported, Refuted, Uncertain, Needs Context
    summary: str

class ChatAgentRequest:
    question: str
    chat_id: int
    query: str
    result: Dict[str, Any]
