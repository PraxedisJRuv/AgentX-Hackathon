from agent.graph import graph
from agent.schema import ReportState
from models import Report, ReportCreate, ReportRead, ReportStatusCreate, ReportStatus
from utils import create_db_and_tables, get_session, save_image, parse_images_to_b64
from clients import JiraClient
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from langgraph.graph.state import CompiledStateGraph
from contextlib import asynccontextmanager
from datetime import datetime
import base64
import json
import os

SessionDep = Annotated[Session, Depends(get_session)]

report_agent: CompiledStateGraph = None
jira_client: JiraClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global report_agent
    global jira_client
    create_db_and_tables()
    report_agent = graph.compile()
    jira_client = JiraClient()
    yield


REPORT_LOG_VALUES = {
    "1": "Report received",
    "2": "Report analysed",
    "3": "The responsible team has been notified",
    "4": "The issue has been taken on by a team member",
    "5": "The issue has been resolved",
}


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def put_report_status(report_id: str, status_id: str, session: Session):
    status = ReportStatus(report_id=report_id, status_id=status_id)
    session.add(status )
    session.commit()
    session.refresh(status)
    return {"message": "Report status updated successfully"}


@app.get("/reports/")
def read_reports(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[ReportRead]:
    reports = session.exec(select(Report).offset(offset).limit(limit)).all()

    report_reads = [ReportRead(**report.model_dump()) for report in reports]

    return report_reads


@app.get("/report/{report_id}")
def read_report(report_id: str, session: SessionDep) -> ReportRead:
    report = session.get(Report, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    images_b64 = parse_images_to_b64(report.images_path)

    report_read = ReportRead(**report.model_dump(), images_b64=images_b64)

    return report_read


@app.post("/reports/")
def create_report(report: ReportCreate, session: SessionDep) -> dict:
    b64_images = report.images_base64
    db_report = Report.model_validate(report)

    images_path_list = [
        save_image(b64, f"{db_report.id}_{i}") for i, b64 in enumerate(b64_images)
    ]
    db_report.images_path = "!".join(images_path_list)

    session.add(db_report)
    session.commit()
    session.refresh(db_report)

    put_report_status(db_report.id, "1", session)

    return {"message": "Report created successfully", "report_id": db_report.id}


@app.post("/reports/{report_id}/run")
async def run_report(report_id: str, session: SessionDep):
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    if report.status != "pending":
        raise HTTPException(status_code=400, detail=f"Report status must be 'pending' to run. Current status: {report.status}")

    report.status = "processing"
    report.updated_at = datetime.today().isoformat()
    session.add(report)
    session.commit()

    put_report_status(report_id, "2", session)

    async def event_generator():
        try:
            initial_state: ReportState = {
                "text": report.description,
                "image_b64": parse_images_to_b64(report.images_path)[0] if report.images_path else None,
                "image_mime": "image/jpeg" if report.images_path else None,
                "urgency_level": None,
                "image_required": None,
                "image_instruction": None,
                "image_condition_met": None,
                "edit_count": 0,
                "final_solution": None,
                "status": None,
                "messages": [],
            }

            async for chunk in report_agent.astream(initial_state, stream_mode="updates"):
                yield f"data: {json.dumps(chunk, default=str)}\n\n"
            report.status = "submitted"
            session.add(report)
            session.commit()

            yield "event: done\ndata: {}\n\n"
        except Exception as e:
            report.status = "failed"
            session.add(report)
            session.commit()
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.delete("/reports/{report_id}")
def delete_report(report_id: str, session: SessionDep):
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    session.delete(report)
    session.commit()
    return {"ok": True}


@app.get("/reports/{report_id}/statuses")
def read_report_statuses(report_id: str, session: SessionDep) -> list[dict]:
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    statuses = session.exec(
        select(ReportStatus).where(ReportStatus.report_id == report_id)
    ).all()
    return [
        {
            "status_id": s.status_id,
            "text": REPORT_LOG_VALUES.get(str(s.status_id), "Unknown status"),
            "created_at": s.created_at,
        }
        for s in statuses
    ]
