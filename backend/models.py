from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import uuid4


class ReportBase(SQLModel):
    name: str = Field(index=True)  # non optional
    description: str
    issue_date: str | None = Field(default=None)


class Report(ReportBase, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    ticket_id: str | None = Field(default=None)
    created_at: str | None = Field(default_factory=lambda: datetime.today().isoformat())
    updated_at: str | None = Field(default_factory=lambda: datetime.today().isoformat())
    status: str | None = Field(default_factory=lambda: "pending")
    images_path: str | None = Field(default=None)


class ReportCreate(ReportBase):
    images_base64: list[str]


class ReportRead(ReportBase):
    id: str
    ticket_id: str | None
    created_at: str
    updated_at: str
    status: str
    images_b64: list[str] | None = Field(default=None)


class ReportStatus(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    report_id: str = Field(index=True)
    status_id: int
    created_at: str | None = Field(default_factory=lambda: datetime.today().isoformat())
