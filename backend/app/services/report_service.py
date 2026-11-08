"""Harassment incident diary service logic."""

from typing import Any

from backend.app.core.exceptions import NotFoundException
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.report_repo import ReportRepository
from backend.app.schemas.report import IncidentCreate, IncidentUpdate


class ReportService:
    def __init__(
        self, report_repo: ReportRepository, audit_repo: AuditRepository
    ) -> None:
        self.report_repo = report_repo
        self.audit_repo = audit_repo

    async def list_reports(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        skip = (page - 1) * page_size
        items = await self.report_repo.list_by_user(user_id, skip=skip, limit=page_size)
        total = await self.report_repo.count_by_user(user_id)
        return items, total

    async def get_report(self, report_id: str, user_id: str) -> dict[str, Any]:
        report = await self.report_repo.get_by_id_and_user(report_id, user_id)
        if not report:
            raise NotFoundException(
                "Incident record not found.", code="REPORT_NOT_FOUND"
            )
        return report

    async def create_report(self, user_id: str, data: IncidentCreate) -> dict[str, Any]:
        doc_data = {
            "user_id": user_id,
            "category": data.category,
            "incident_date": data.incident_date,
            "location_summary": (
                data.location_summary.strip() if data.location_summary else None
            ),
            "notes": data.notes.strip(),
            "witnesses": data.witnesses.strip() if data.witnesses else None,
            "evidence_files": [],
        }
        report = await self.report_repo.create(doc_data)
        await self.audit_repo.log_action(
            action="INCIDENT_REPORTED",
            resource="incident_reports",
            actor_id=user_id,
            resource_id=report["id"],
        )
        return report

    async def update_report(
        self, report_id: str, user_id: str, data: IncidentUpdate
    ) -> dict[str, Any]:
        existing = await self.report_repo.get_by_id_and_user(report_id, user_id)
        if not existing:
            raise NotFoundException(
                "Incident record not found.", code="REPORT_NOT_FOUND"
            )

        update_dict: dict[str, Any] = {}
        if data.category is not None:
            update_dict["category"] = data.category
        if data.incident_date is not None:
            update_dict["incident_date"] = data.incident_date
        if data.location_summary is not None:
            update_dict["location_summary"] = (
                data.location_summary.strip() if data.location_summary else None
            )
        if data.notes is not None:
            update_dict["notes"] = data.notes.strip()
        if data.witnesses is not None:
            update_dict["witnesses"] = (
                data.witnesses.strip() if data.witnesses else None
            )

        updated = await self.report_repo.update_by_user(report_id, user_id, update_dict)
        if not updated:
            raise NotFoundException(
                "Incident record not found.", code="REPORT_NOT_FOUND"
            )

        await self.audit_repo.log_action(
            action="INCIDENT_UPDATED",
            resource="incident_reports",
            actor_id=user_id,
            resource_id=report_id,
        )
        return updated

    async def delete_report(self, report_id: str, user_id: str) -> None:
        existing = await self.report_repo.get_by_id_and_user(report_id, user_id)
        if not existing:
            raise NotFoundException(
                "Incident record not found.", code="REPORT_NOT_FOUND"
            )

        success = await self.report_repo.delete_by_user(report_id, user_id)
        if not success:
            raise NotFoundException(
                "Incident record not found.", code="REPORT_NOT_FOUND"
            )

        await self.audit_repo.log_action(
            action="INCIDENT_DELETED",
            resource="incident_reports",
            actor_id=user_id,
            resource_id=report_id,
        )
