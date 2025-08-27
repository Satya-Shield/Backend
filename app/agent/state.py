from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages:Annotated[list,add_messages]
    input_text: str
    claims: List[str]
    evidence: Dict[str,Any]
    verdicts: Dict[str,Any]
    explanations: Dict[str,str]
