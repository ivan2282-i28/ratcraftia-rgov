from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from ..core.security import get_current_user
from ..db import get_session
from ..models import User
from ..schemas import MailCreate, MailRead
from ..services.portal import list_mail, send_mail


router = APIRouter(prefix="/api/mail", tags=["mail"])


@router.get("/messages", response_model=list[MailRead])
def get_messages(
    box: str = Query(default="inbox", pattern="^(inbox|sent)$"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[MailRead]:
    return list_mail(session, user, box)


@router.post("/messages", response_model=MailRead, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MailCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MailRead:
    try:
        return send_mail(session, user, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
