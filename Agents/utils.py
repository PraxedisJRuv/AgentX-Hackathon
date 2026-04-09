def read_json():
    #para leer lo que debería del JSON
    return 0


def build_image_for_API():
    return 0


def run_report(text: str,image_path: Optional[str] = None,edit_count: int = 0,) -> ReportState:
    
    image_b64, image_mime = (None, None)
    
    """
    if image_path:
        image_b64, image_mime = load_image(image_path)

    """
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
    