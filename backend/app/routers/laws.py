from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Law
from ..schemas import LawRead
from ..services.portal import serialize_law


router = APIRouter(prefix="/api/laws", tags=["laws"])


@router.get("", response_model=list[LawRead])
def list_laws(session: Session = Depends(get_session)) -> list[LawRead]:
    laws = session.exec(select(Law).order_by(Law.level.desc(), Law.updated_at.desc())).all()
    return [serialize_law(law) for law in laws]
