from typing_extensions import TypedDict
from typing import List, Dict, Any

class State(TypedDict):
    claims: List[str]
    evidence: Dict[str, Any]
    claim_verdicts: Dict[str, Any]
    confidence_scores: Dict[str, Any]
    result: Dict[str, Any]
    overall: Dict[str, Any]
    
