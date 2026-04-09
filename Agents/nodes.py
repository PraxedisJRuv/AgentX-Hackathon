import utils as ut
from schemas import ReportState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

MAX_EDITS = 3


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

    if state.get("image_condition_met"):
        return "propose_solution"

    if state.get("edit_count", 0) >= MAX_EDITS:
        return "stop_process"

    return "request_image_again"


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


