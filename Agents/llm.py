#pip install -U google-generativeai
import google.generativeai as genai
from langgraph.graph import END, StateGraph
from typing import Annotated, Optional, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import utils as ut

MAX_EDITS = 3

#Falta checar todo sobre cómo conectarse 
genai.configure(api_key="YOUR_API_KEY")
llm = genai.GenerativeModel(model="gemini-2.5-flash", temperature=0)


#El esquema para todo el reporte
class ReportState(TypedDict):
    #Inputs
    text: str
    image_b64: Optional[str]           
    image_type: str

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

#Vamos a necistar la función para mandar las imagenes correctamente y revisar cómo
#img = PIL.Image.open('path/imagen.jpg') parece servir en la documentación si import PIL.Image
def build_image_for_API():
    return 0

#función para leer los json de las repuestas de texto y ver cómo las mandan
def read_json():
    return 0








def build_graph() -> StateGraph:
    graph = StateGraph(ReportState)

    graph.add_node("evaluate_report", evaluate_report)
    graph.add_node("request_image", request_image)
    graph.add_node("generate_image_instruction", generate_image_instruction)
    graph.add_node("analyze_image", analyze_image)
    graph.add_node("request_report_edit", request_image_again)
    graph.add_node("propose_solution", propose_solution)
    graph.add_node("stop_process", stop_process)

    graph.set_entry_point("evaluate_report")

    graph.add_conditional_edges("evaluate_report",route_after_evaluation,
        {
            "request_image": "request_image",
            "generate_image_instruction": "generate_image_instruction",
            "propose_solution": "propose_solution",
        },
    )

    # Después de pedir imagen el usuario debe re-enviar → volver a evaluar
    graph.add_edge("request_image", END)  # Interrupción: espera al usuario

    # Cadena de análisis de imagen
    graph.add_edge("generate_image_instruction", "analyze_image")

    graph.add_conditional_edges("analyze_image",route_after_image_analysis,
        {
            "propose_solution": "propose_solution",
            "request_report_edit": "request_report_edit",
            "stop_process": "stop_process",
        },
    )

    #No estoy tan seguro que se envíe bien cuando se terminan los intentos
    graph.add_edge("request_report_edit", END)  


    graph.add_edge("propose_solution", END)
    graph.add_edge("stop_process", END)

    return graph


compiled_graph = build_graph().compile()


def request_image(state: ReportState) -> ReportState:
    msg = (
        "To propperly deal with the report, an image of the issue is needed. "
        "Please attach an image to continue the report submission"
    )
    return {
        **state,
        "status": msg,
        "messages": [AIMessage(content=msg)],
    }


def request_image_again(state: ReportState) -> ReportState:
    
    new_count = state["edit_count"] + 1
    msg = (
        f"La imagen proporcionada no cumple la condición requerida. "
        f"Por favor edita el reporte e intenta de nuevo. "
        f"(Intento {new_count}/{MAX_EDITS})"
    )
    return {
        **state,
        "edit_count": new_count,
        "image_condition_met": None,   # Resetear para la próxima ronda
        "messages": [AIMessage(content=msg)],
        "status": msg,
    }


def stop_process(state: ReportState) -> ReportState:
    msg = (
        "A chingar a tu madre"
    )
    return {
        **state,
        "status": msg,
        "messages": [AIMessage(content=msg)],
    }


def route_after_evaluation(state: ReportState) -> str:

    image_required: bool = state.get("image_required", False)
    has_image: bool = bool(state.get("image_b64"))

    if image_required and not has_image:
        return "request_image"

    if has_image:
        return "generate_image_instruction"

    return "propose_solution"

def route_after_image_analysis(state: ReportState) -> str:
    #Análisis post-imagen
    if state.get("image_condition_met"):
        return "propose_solution"

    # Si mentiroso
    if state.get("edit_count", 0) >= MAX_EDITS:
        return "stop_process"

    return "request_report_edit"

def evaluate_report(state: ReportState) -> ReportState:
  #Que la misma LLM al mismo tiempo evalúe urgencia y necesidad de imagen, entre otros...
    system = SystemMessage(content=(
        #No sé bien qué escribir pero son instrucciones para el LLM, no sé ni en qué idioma (inglés obvio)
        "Las instrucciones para este paso de la IA"
    ))
    human = HumanMessage(content=f"Reporte:\n{state['text']}")

    response = llm.invoke([system, human])
    parsed = ut.read_json(response.content)

    return {
        **state,
        "urgency_level": parsed.get("urgency_level", "medium"),
        "image_required": parsed.get("image_required", False),
        "messages": [
            AIMessage(content=(
                f"[Evaluation] Urgeny: {parsed.get('urgency_level')} | "
                f"Requiered image: {parsed.get('image_required')} | "
                f"Reason: {parsed.get('reasoning')}"
            ))
        ],
    }


def generate_image_instruction(state: ReportState) -> ReportState:

    system = SystemMessage(content=(
        "Las instrucciones para el análisis. Especificar el JSON y que no debe salirse"
    ))
    human = HumanMessage(content=f"Report text:\n{state['text']}")

    response = llm.invoke([system, human])
    parsed = ut.read_json(response.content)

    instruction = parsed.get("instruction", "Analyzed the attached image")
    return {
        **state,
        "image_instruction": instruction,
        "messages": [
            AIMessage(content=f"[Analysis instruction] {instruction}")
        ],
    }


def analyze_image(state: ReportState) -> ReportState:

    instruction = state["image_instruction"] or "Analiza la imagen adjunta."
    system = SystemMessage(content=(
        
        "prompt que condicione a JSON booleano"

    ))

    content: list = [{"type": "text", "text": f"Instrucción: {instruction}"},]

    if state.get("image_b64"):
        content.append(ut.build_image_for_API(state["image_b64"]))

    human = HumanMessage(content=content)
    response = llm.invoke([system, human])
    parsed = ut.read_json(response.content)

    condition_met: bool = bool(parsed.get("condition_met", False))
    explanation: str = parsed.get("explanation", "without explanation")

    return {
        **state,
        "image_condition_met": condition_met,
        "messages": [
            AIMessage(content=(
                f"[image analysis] condition met: {condition_met} | "
                f"Explicación: {explanation}"
            ))
        ],
    }


def propose_solution(state: ReportState) -> ReportState:
    context_parts = [
        f"report text:\n{state['text']}",
        f"Urgency level: {state.get('urgency_level', 'unkown')}",
    ]
    if state.get("image_instruction"):
        context_parts.append(f"image analysis: {state.get('image_instruction')}")

    context = "\n\n".join(context_parts)

    system = SystemMessage(content=(
        
        "Prompt para ser experto en incidentes"
    
    ))

    human = HumanMessage(content=context)
    response = llm.invoke([system, human])

    solution = response.content
    return {
        **state,
        "final_solution": solution,
        "status": "Completed",
        "messages": [AIMessage(content=f"[Proposed solution]\n\n{solution}")],
    }