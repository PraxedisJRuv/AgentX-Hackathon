from agent.schema import ReportState, MAX_EDITS 


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