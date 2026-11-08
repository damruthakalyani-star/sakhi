"""Incident reporting and evidence diary endpoints."""

from typing import Any

from backend.app.api.deps import get_current_user, get_report_service
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.report import IncidentCreate, IncidentResponse, IncidentUpdate
from backend.app.services.report_service import ReportService
from fastapi import APIRouter, Depends, Query, Response, status

router = APIRouter()


@router.get(
    "/incidents",
    response_model=PaginatedResponse[IncidentResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's recorded incident diary entries",
)
async def list_incidents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict[str, Any] = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[IncidentResponse]:
    items, total = await report_service.list_reports(
        current_user["id"], page=page, page_size=page_size
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse[IncidentResponse](
        items=[IncidentResponse(**i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new incident diary entry",
)
async def create_incident(
    data: IncidentCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> IncidentResponse:
    report = await report_service.create_report(current_user["id"], data)
    return IncidentResponse(**report)


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single incident diary entry",
)
async def get_incident(
    incident_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> IncidentResponse:
    report = await report_service.get_report(incident_id, current_user["id"])
    return IncidentResponse(**report)


@router.put(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing incident entry",
)
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> IncidentResponse:
    report = await report_service.update_report(incident_id, current_user["id"], data)
    return IncidentResponse(**report)


@router.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an incident entry",
)
async def delete_incident(
    incident_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service),
) -> Response:
    await report_service.delete_report(incident_id, current_user["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
