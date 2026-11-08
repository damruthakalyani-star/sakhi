"""Emergency SOS Assistance endpoints."""

from typing import Any

from backend.app.api.deps import get_current_user, get_sos_service
from backend.app.schemas.sos import (
    ActiveSOSStatus,
    SOSResolveRequest,
    SOSResponse,
    SOSTriggerRequest,
)
from backend.app.services.sos_service import SOSService
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post(
    "/trigger",
    response_model=SOSResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger Emergency SOS alert",
)
async def trigger_sos(
    data: SOSTriggerRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    sos_service: SOSService = Depends(get_sos_service),
) -> SOSResponse:
    sos = await sos_service.trigger_sos(current_user["id"], data)
    return SOSResponse(**sos)


@router.get(
    "/active",
    response_model=ActiveSOSStatus,
    status_code=status.HTTP_200_OK,
    summary="Get status of currently active SOS alert",
)
async def get_active_sos(
    current_user: dict[str, Any] = Depends(get_current_user),
    sos_service: SOSService = Depends(get_sos_service),
) -> ActiveSOSStatus:
    active = await sos_service.get_active_sos(current_user["id"])
    if active:
        return ActiveSOSStatus(has_active_sos=True, sos=SOSResponse(**active))
    return ActiveSOSStatus(has_active_sos=False, sos=None)


@router.post(
    "/resolve",
    response_model=SOSResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve or cancel an active SOS alert",
)
async def resolve_sos(
    data: SOSResolveRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    sos_service: SOSService = Depends(get_sos_service),
) -> SOSResponse:
    resolved = await sos_service.resolve_sos(current_user["id"], data.resolution_note)
    return SOSResponse(**resolved)
