from typing import Optional, TypedDict, Annotated
from langgraph.graph import add_messages
    
MAX_EDITS = 3

class ReportState(TypedDict):
    #Inputs
    text: str
    image_b64: Optional[str]           
    image_mime: Optional[str]

    #Análisis
    urgency_level: Optional[str]
    image_required: Optional[bool]
    image_instruction: Optional[str]
    image_condition_met: Optional[bool]

    stop_reason: Optional[str]

    #Controles
    edit_count: int
    final_solution: Optional[str]
    status: Optional[str]

    #Historial de la conversación
    messages: Annotated[list, add_messages]