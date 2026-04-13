from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.security import get_current_user
from ..db import get_session
from ..models import User
from ..schemas import (
    MessageResponse,
    PushConfigResponse,
    PushSubscriptionCreate,
    PushSubscriptionRemove,
)
from ..services.notifications import (
    get_push_config,
    register_push_subscription,
    unregister_push_subscription,
)


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/config", response_model=PushConfigResponse)
def get_config(user: User = Depends(get_current_user)) -> PushConfigResponse:
    del user
    return get_push_config()


@router.post("/subscriptions", response_model=MessageResponse)
def subscribe(
    payload: PushSubscriptionCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    try:
        register_push_subscription(
            session,
            user_id=user.id,
            subscription=payload.subscription,
            user_agent=payload.user_agent,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return MessageResponse(detail="Push-уведомления подключены.")


@router.post("/subscriptions/unregister", response_model=MessageResponse)
def unsubscribe(
    payload: PushSubscriptionRemove,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    unregister_push_subscription(session, user_id=user.id, endpoint=payload.endpoint)
    return MessageResponse(detail="Push-уведомления отключены.")
