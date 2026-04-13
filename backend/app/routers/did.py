from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..core.security import create_did_token, get_current_user
from ..db import get_session
from ..models import User
from ..schemas import DidTokenResponse, ProfileResponse
from ..services.portal import serialize_profile


router = APIRouter(prefix="/api/did", tags=["did"])


@router.get("/me", response_model=ProfileResponse)
def did_profile(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    return serialize_profile(session, user)


@router.get("/me/token", response_model=DidTokenResponse)
def did_token(user: User = Depends(get_current_user)) -> DidTokenResponse:
    token, expires_at, payload = create_did_token(user)
    return DidTokenResponse(token=token, expires_at=expires_at, payload=payload)
