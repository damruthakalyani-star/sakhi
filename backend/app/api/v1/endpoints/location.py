"""Live location sharing endpoints."""

from typing import Any

from backend.app.api.deps import get_current_user, get_location_service
from backend.app.schemas.location import (
    LocationShareRequest,
    LocationShareResponse,
    PublicSharedLocationView,
)
from backend.app.services.location_service import LocationService
from fastapi import APIRouter, Depends, Response, status

router = APIRouter()


@router.post(
    "/share",
    response_model=LocationShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or refresh live location sharing session",
)
async def share_location(
    data: LocationShareRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    location_service: LocationService = Depends(get_location_service),
) -> LocationShareResponse:
    res = await location_service.share_location(current_user["id"], data)
    return LocationShareResponse(**res)


@router.get(
    "/shared/{share_token}",
    response_model=PublicSharedLocationView,
    status_code=status.HTTP_200_OK,
    summary="View live location via secure share token (Public Gated)",
)
async def view_shared_location(
    share_token: str,
    location_service: LocationService = Depends(get_location_service),
) -> PublicSharedLocationView:
    return await location_service.get_shared_location(share_token)


@router.delete(
    "/share",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Stop active location sharing",
)
async def stop_location_sharing(
    current_user: dict[str, Any] = Depends(get_current_user),
    location_service: LocationService = Depends(get_location_service),
) -> Response:
    await location_service.stop_sharing(current_user["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
