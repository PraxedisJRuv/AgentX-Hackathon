from models import Report, ReportCreate, ReportRead, ReportStatus
from utils import create_db_and_tables, get_session, save_image, parse_images_to_b64
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import base64
import os

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


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
    return {"message": "Report created successfully", "report_id": db_report.id}


@app.delete("/reports/{report_id}")
def delete_report(report_id: str, session: SessionDep):
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    session.delete(report)
    session.commit()
    return {"ok": True}
