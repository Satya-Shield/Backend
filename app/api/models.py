from pydantic import BaseModel
from typing import List, Optional

class AgentRequest(BaseModel):
    query: str
    image: Optional[str] = None
    video: Optional[str] = None


class AgentResponse(BaseModel):
    claim: str
    verdict: str               # One of: Supported, Refuted, Uncertain, Needs Context
    confidence: int            # Integer from 0–100
    explanation: str           # 120–180 words explanation with citations
    sources: List[str]         # List of source URLs or identifiers
    techniques: List[str]      # Manipulative techniques detected
    checklist: List[str]       # 3-step user action checklist
