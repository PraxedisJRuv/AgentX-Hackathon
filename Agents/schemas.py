from typing import Annotated, Optional, TypedDict
from langgraph.graph.message import add_messages

class ReportState(TypedDict):
    #Inputs
    text: str
    image_b64: Optional[str]           
    image_type: Optional[str]

    #Análisis
    urgency_level: Optional[str]
    image_required: Optional[bool]
    image_instruction: Optional[str]
    image_condition_met: Optional[bool]

    #Controles
    edit_count: int
    final_solution: Optional[str]
    status: Optional[str]

    #Historial de la conversación
    messages: Annotated[list, add_messages]