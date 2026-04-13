from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.security import get_current_user
from ..db import get_session
from ..models import User
from ..schemas import (
    RatublesMintRequest,
    RatublesTransactionRead,
    RatublesTransferRequest,
    UserDirectoryRead,
)
from ..services.portal import (
    list_all_transactions,
    list_transfer_directory,
    list_user_transactions,
    mint_ratubles,
    transfer_ratubles,
)


router = APIRouter(prefix="/api/ratubles", tags=["ratubles"])


@router.get("/directory", response_model=list[UserDirectoryRead])
def get_directory(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[UserDirectoryRead]:
    return list_transfer_directory(session)


@router.get("/transactions", response_model=list[RatublesTransactionRead])
def get_transactions(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[RatublesTransactionRead]:
    return list_user_transactions(session, user)


@router.get("/ledger", response_model=list[RatublesTransactionRead])
def get_ledger(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[RatublesTransactionRead]:
    try:
        return list_all_transactions(session, user)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.post("/transfer", response_model=RatublesTransactionRead, status_code=status.HTTP_201_CREATED)
def create_transfer(
    payload: RatublesTransferRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> RatublesTransactionRead:
    try:
        return transfer_ratubles(session, user, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/mint", response_model=RatublesTransactionRead, status_code=status.HTTP_201_CREATED)
def create_mint(
    payload: RatublesMintRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> RatublesTransactionRead:
    try:
        return mint_ratubles(session, user, payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
