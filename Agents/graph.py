import nodes as nd
from langgraph.graph import END, StateGraph
from schemas import ReportState


def build_graph() -> StateGraph:
    graph = StateGraph(ReportState)

    graph.add_node("evaluate_report", nd.evaluate_report)
    graph.add_node("request_image", nd.request_image)
    graph.add_node("generate_image_instruction", nd.generate_image_instruction)
    graph.add_node("analyze_image", nd.analyze_image)
    graph.add_node("request_report_edit", nd.request_image_again)
    graph.add_node("propose_solution", nd.propose_solution)
    graph.add_node("stop_process", nd.stop_process)

    graph.set_entry_point("evaluate_report")

    graph.add_conditional_edges("evaluate_report", nd.route_after_evaluation,
        {
            "request_image": "request_image",
            "generate_image_instruction": "generate_image_instruction",
            "propose_solution": "propose_solution",
        },
    )

    graph.add_edge("request_image", END) 

    # Cadena de análisis de imagen
    graph.add_edge("generate_image_instruction", "analyze_image")

    graph.add_conditional_edges("analyze_image",nd.route_after_image_analysis,
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

