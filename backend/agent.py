import asyncio
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph


class ReportState(TypedDict):
    report_id: str
    logs: list[str]


async def running_analysis(state: ReportState) -> dict:
    await asyncio.sleep(2)
    return {"logs": state["logs"] + ["Running analysis..."]}


async def analyzing_images(state: ReportState) -> dict:
    await asyncio.sleep(2)
    return {"logs": state["logs"] + ["Analyzing images..."]}


async def analyzing_solutions(state: ReportState) -> dict:
    await asyncio.sleep(2)
    return {"logs": state["logs"] + ["Analyzing solutions..."]}


graph = StateGraph(ReportState)

graph.add_node("running_analysis", running_analysis)
graph.add_node("analyzing_images", analyzing_images)
graph.add_node("analyzing_solutions", analyzing_solutions)

graph.add_edge(START, "running_analysis")
graph.add_edge("running_analysis", "analyzing_images")
graph.add_edge("analyzing_images", "analyzing_solutions")
graph.add_edge("analyzing_solutions", END)

report_graph = graph.compile()
