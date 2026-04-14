from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.security import get_current_user
from ..db import get_session
from ..models import User
from ..schemas import (
    DeveloperAppCreate,
    DeveloperAppCreateResponse,
    DeveloperAppRead,
    DeveloperAppSecretResponse,
)
from ..services.oauth import list_developer_apps, oauth_scope_catalog, register_developer_app, rotate_developer_app_secret


router = APIRouter(prefix="/api/developer", tags=["developer"])


@router.get("/scopes")
def get_oauth_scopes() -> list[dict[str, str]]:
    return oauth_scope_catalog()


@router.get("/apps", response_model=list[DeveloperAppRead])
def get_my_apps(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[DeveloperAppRead]:
    return list_developer_apps(session, user)


@router.post("/apps", response_model=DeveloperAppCreateResponse, status_code=status.HTTP_201_CREATED)
def create_app(
    payload: DeveloperAppCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DeveloperAppCreateResponse:
    try:
        return register_developer_app(session, user, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/apps/{app_id}/rotate-secret", response_model=DeveloperAppSecretResponse)
def rotate_app_secret(
    app_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DeveloperAppSecretResponse:
    try:
        return rotate_developer_app_secret(session, user, app_id)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
