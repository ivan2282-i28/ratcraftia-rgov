from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.security import get_current_user
from ..db import get_session
from ..models import Referendum, User
from ..schemas import ReferendumCreate, ReferendumOutcomeRead, ReferendumRead, VoteRequest
from ..services.portal import (
    create_referendum,
    publish_referendum,
    serialize_referendum,
    sign_referendum,
    vote_referendum,
)


router = APIRouter(prefix="/api/referenda", tags=["referenda"])


@router.get("", response_model=list[ReferendumRead])
def list_referenda(session: Session = Depends(get_session)) -> list[ReferendumRead]:
    referenda = session.exec(select(Referendum).order_by(Referendum.created_at.desc())).all()
    return [serialize_referendum(session, referendum) for referendum in referenda]


@router.post("", response_model=ReferendumRead, status_code=status.HTTP_201_CREATED)
def new_referendum(
    payload: ReferendumCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReferendumRead:
    try:
        return create_referendum(session, user, payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/{referendum_id}/vote", response_model=ReferendumRead)
def cast_referendum_vote(
    referendum_id: int,
    payload: VoteRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReferendumRead:
    try:
        return vote_referendum(session, user, referendum_id, payload.vote)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/{referendum_id}/sign", response_model=ReferendumRead)
def add_referendum_signature(
    referendum_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReferendumRead:
    try:
        return sign_referendum(session, user, referendum_id)
    except (PermissionError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/{referendum_id}/publish", response_model=ReferendumOutcomeRead)
def enact_referendum(
    referendum_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReferendumOutcomeRead:
    try:
        return publish_referendum(session, user, referendum_id)
    except (PermissionError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
