import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, StateGraph
from typing import Annotated, Optional, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0,api_key=api_key)

GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
GITHUB_REPO  = "reactioncommerce/reaction"

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


def read_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No se encontró JSON en: {text}")
    return json.loads(text[start:end])


def build_image_for_API(b64:str, mime:str)-> dict:
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime};base64,{b64}"},
    }


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


async def propose_solution(state: ReportState) -> ReportState:
    print("at propose solution")
    context_parts = [
        f"report text:\n{state['text']}",
        f"Urgency level: {state.get('urgency_level', 'unkown')}",
    ]
    if state.get("image_instruction"):
        context_parts.append(f"image analysis: {state.get('image_instruction')}")

    context = "\n\n".join(context_parts)
    mcp_client=MultiServerMCPClient({
    "github": {
        "command": "docker",
        "args": [
            "run", "-i", "--rm",
            "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={GITHUB_TOKEN}",
            "ghcr.io/github/github-mcp-server"
        ],
        "transport": "stdio",
         }
    })
        
    github_tools = await mcp_client.get_tools()
    print(f"Herramientas disponibles: {[t.name for t in github_tools]}")


    system_prompt=(
        
        "Eres un experto en gestión de incidentes y desarrollo de software. "
            f"Tienes acceso al repositorio de GitHub '{GITHUB_REPO}' mediante herramientas. "
            "ANTES de proponer una solución, debes:\n"
            "  1. Explorar la estructura del repositorio.\n"
            "  2. Leer los archivos más relevantes para el problema reportado.\n"
            "  3. Entender el código real de la aplicación.\n\n"
            "Luego, genera una solución clara, estructurada y accionable que "
            "referencie archivos y fragmentos de código específicos del repositorio. "
            "Considera el nivel de urgencia en tu respuesta."

    )
    agent = create_agent(
            model=llm,
            tools=github_tools,
            system_prompt=system_prompt
        )
    
    print(" explorando repositorio")
    result = await agent.ainvoke({
            "messages": [HumanMessage(content=context)]
        })
    
    solution = result["messages"][-1].content
    print(f" Solución generada ({len(solution)} chars)")

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


def route_after_evaluation(state: ReportState) -> str:
    print("at route after evaluation")
    image_required: bool = state.get("image_required", False)
    has_image: bool = bool(state.get("image_b64"))

    if image_required and not has_image:
        return "request_image"

    if has_image:
        return "generate_image_instruction"

    return "propose_solution"


def route_after_image_analysis(state: ReportState) -> str:
    print("at route after image analysis")
    if state.get("image_condition_met"):
        return "propose_solution"

    if state.get("edit_count", 0) >= MAX_EDITS:
        
        return "stop_process"

    return "request_report_edit"


def build_graph() -> StateGraph:
    graph = StateGraph(ReportState)

    graph.add_node("evaluate_report", evaluate_report)
    graph.add_node("request_image", request_image)
    graph.add_node("generate_image_instruction", generate_image_instruction)
    graph.add_node("analyze_image", analyze_image)
    graph.add_node("request_report_edit", request_report_edit)
    graph.add_node("propose_solution", propose_solution)
    graph.add_node("stop_process", stop_process)

    graph.set_entry_point("evaluate_report")

    graph.add_conditional_edges("evaluate_report", route_after_evaluation,
        {
            "request_image": "request_image",
            "generate_image_instruction": "generate_image_instruction",
            "propose_solution": "propose_solution",
        },
    )

    graph.add_edge("request_image", END) 

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

#La verdadera corrida:
import base64
from pathlib import Path

compiled_graph = build_graph().compile()

def load_image_as_b64(path: str) -> tuple[str, str]:
    ext_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
    p = Path(path)
    mime = ext_map.get(p.suffix.lower(), "image/jpeg")
    data = base64.b64encode(p.read_bytes()).decode()
    return data, mime


async def run_report( text: str, image_path: Optional[str] = None, edit_count: int = 0,) -> ReportState:

    image_b64, image_mime = (None, "image/jpeg")
    if image_path:
        image_b64, image_mime = load_image_as_b64(image_path)

    initial_state: ReportState = {
        "text": text,
        "image_b64": image_b64,
        "image_mime": image_mime,
        "urgency_level": None,
        "image_required": None,
        "image_instruction": None,
        "image_condition_met": None,
        "edit_count": edit_count,
        "final_solution": None,
        "status": None,
        "messages": [],
    }

    result = await compiled_graph.ainvoke(initial_state)
    return result

if __name__=="__main__":

    sample_text = (
            "La página es demasiado lenta al revisar los productos."
        )

    state1 = asyncio.run(run_report(text=sample_text,image_path=None,))
    print(state1)

    """
    for msg in state1["messages"]:
            role = "IAlexis" if isinstance(msg, AIMessage) else "Humano"
            print(f"{role}: {msg.content}\n")
    """