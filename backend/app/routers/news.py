from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.security import get_current_user
from ..db import get_session
from ..models import NewsPost, User
from ..schemas import MessageResponse, NewsCreate, NewsRead
from ..services.portal import delete_news, post_news, serialize_news


router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=list[NewsRead])
def list_news(session: Session = Depends(get_session)) -> list[NewsRead]:
    news = session.exec(select(NewsPost).order_by(NewsPost.created_at.desc())).all()
    return [serialize_news(session, item) for item in news]


@router.post("", response_model=NewsRead, status_code=status.HTTP_201_CREATED)
def create_news(
    payload: NewsCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> NewsRead:
    try:
        return post_news(session, user, payload)
    except (PermissionError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.delete("/{news_id}", response_model=MessageResponse)
def remove_news(
    news_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    try:
        delete_news(session, user, news_id)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return MessageResponse(detail="Новость удалена.")
