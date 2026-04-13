from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.security import get_current_user
from ..db import get_session
from ..models import Bill, User
from ..schemas import BillCreate, BillRead, LawRead, VoteRequest
from ..services.portal import create_bill, publish_bill, serialize_bill, vote_bill


router = APIRouter(prefix="/api/parliament", tags=["parliament"])


@router.get("/bills", response_model=list[BillRead])
def list_bills(session: Session = Depends(get_session)) -> list[BillRead]:
    bills = session.exec(select(Bill).order_by(Bill.created_at.desc())).all()
    return [serialize_bill(session, bill) for bill in bills]


@router.post("/bills", response_model=BillRead, status_code=status.HTTP_201_CREATED)
def new_bill(
    payload: BillCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BillRead:
    try:
        return create_bill(session, user, payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/bills/{bill_id}/vote", response_model=BillRead)
def cast_bill_vote(
    bill_id: int,
    payload: VoteRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BillRead:
    try:
        return vote_bill(session, user, bill_id, payload.vote)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/bills/{bill_id}/publish", response_model=LawRead)
def enact_bill(
    bill_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> LawRead:
    try:
        return publish_bill(session, user, bill_id)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
