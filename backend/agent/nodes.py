from agent.schema import ReportState, MAX_EDITS
from utils import read_json, build_image_for_API
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0,api_key=api_key)


def evaluate_report(state: ReportState) -> ReportState:

    print("At evaluate_report")
    system = SystemMessage(content=(
        "Eres un sistema experto en análisis de reportes de incidentes de e-commcerce "
        "Recibirás el texto de un reporte y deberás responder ÚNICAMENTE con un "
        "objeto JSON con las siguientes claves:\n"
        '  "urgency_level": "low" | "medium" | "high" | "critical"\n'
        '  "image_required": true | false   (¿es indispensable una imagen?)\n'
        '  "reasoning": "breve explicación"\n'
        "No agregues nada fuera del JSON."
    ))
    human = HumanMessage(content=f"Reporte:\n{state['text']}")

    response = llm.invoke([system, human])
    print(f"reponse: {response}")
    parsed = read_json(response.content)

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


def request_image(state: ReportState) -> ReportState:
    print("At request_image")
    msg = (
        "To propperly deal with the report, an image of the issue is needed. "
        "Please attach an image to continue the report submission"
    )
    return {
        **state,
        "status": msg,
        "messages": [AIMessage(content=msg)],
        "stop_reason":"An image is needed to proceed"
    }


def request_report_edit(state: ReportState) -> ReportState:
    print("At request_report_edit")
    new_count = state["edit_count"] + 1
    msg = (
        f"The attached image doesn't fit the needs for the current report "
        f"Please edit the report and try again "
        f"(Intento {new_count}/{MAX_EDITS})"
    )
    return {
        **state,
        "edit_count": new_count,
        "image_condition_met": None,   # Resetear para la próxima ronda
        "messages": [AIMessage(content=msg)],
        "status": msg,
        "stop_reason":"User must re-upload the image to propperly continue with the report"
    }


def generate_image_instruction(state: ReportState) -> ReportState:
    print("at generate image construction")
    system = SystemMessage(content=(

        "Eres un sistema experto en análisis de reportes de e-commerce con "
        "soporte visual. A partir del texto del reporte, genera una instrucción "
        "clara y concisa para analizar la imagen adjunta. La instrucción debe:\n"
        "  1. Describir qué buscar en la imagen.\n"
        "  2. Definir una condición booleana específica (verdadero/falso) que "
        "     determinará si la imagen es válida para el reporte.\n"
        "Responde ÚNICAMENTE con un JSON:\n"
        '  {"instruction": "...", "condition_description": "..."}\n'
        "No agregues nada fuera del JSON."
        
    ))
    human = HumanMessage(content=f"Report text:\n{state['text']}")

    response = llm.invoke([system, human])
    print(f"reponse: {response}")
    parsed = read_json(response.content)

    instruction = parsed.get("instruction", "Analyzed the attached image")
    return {
        **state,
        "image_instruction": instruction,
        "messages": [
            AIMessage(content=f"[Analysis instruction] {instruction}")
        ],
    }


def analyze_image(state: ReportState) -> ReportState:
    print("at analyze image")
    instruction = state["image_instruction"] or "Analiza la imagen adjunta."
    system = SystemMessage(content=(
        
        "Eres un sistema de análisis visual de reportes. "
        "Recibirás una imagen y una instrucción de análisis. "
        "Responde ÚNICAMENTE con un JSON:\n"
        '  {"condition_met": true | false, "explanation": "..."}\n'
        "No agregues nada fuera del JSON."

    ))

    content: list = [{"type": "text", "text": f"Instrucción: {instruction}"},]

    if state.get("image_b64"):
        content.append(build_image_for_API(state["image_b64"],state["image_mime"]))

    human = HumanMessage(content=content)
    response = llm.invoke([system, human])
    print(f"reponse: {response}")
    parsed = read_json(response.content)

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
    print("at propose solution")
    context_parts = [
        f"report text:\n{state['text']}",
        f"Urgency level: {state.get('urgency_level', 'unkown')}",
    ]
    if state.get("image_instruction"):
        context_parts.append(f"image analysis: {state.get('image_instruction')}")

    context = "\n\n".join(context_parts)

    system = SystemMessage(content=(
        
        "Eres un experto en gestión de incidentes. "
        "Basándote en el reporte proporcionado, genera una solución clara, "
        "estructurada y accionable para resolver el problema. "
        "Considera el nivel de urgencia en tu respuesta."
    
    ))

    human = HumanMessage(content=context)
    response = llm.invoke([system, human])
    print(f"reponse: {response}")
    solution = response.content
    return {
        **state,
        "final_solution": solution,
        "status": "Completed",
        "messages": [AIMessage(content=f"[Proposed solution]\n\n{solution}")],
        "stop_reason": "solved/ solution founded"
    }


def stop_process(state: ReportState) -> ReportState:
    print("At stop process")
    msg = (
        "A chingar a tu madre"
    )
    return {
        **state,
        "status": msg,
        "messages": [AIMessage(content=msg)],
        "stop_reason": "The user wasted all tries"
    }