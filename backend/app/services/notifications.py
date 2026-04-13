from __future__ import annotations

import json
import logging
from typing import Iterable

from pywebpush import WebPushException, webpush
from sqlmodel import Session, select

from ..core.config import get_settings
from ..models import PushSubscription, utc_now
from ..schemas import PushConfigResponse


logger = logging.getLogger(__name__)


def get_push_config() -> PushConfigResponse:
    settings = get_settings()
    return PushConfigResponse(
        public_vapid_key=settings.push_public_key,
        contact_email=settings.push_contact_email,
    )


def register_push_subscription(
    session: Session,
    *,
    user_id: int,
    subscription: dict[str, object],
    user_agent: str = "",
) -> PushSubscription:
    endpoint, serialized = _serialize_subscription(subscription)
    record = session.exec(
        select(PushSubscription).where(PushSubscription.endpoint == endpoint)
    ).first()
    if record:
        record.user_id = user_id
        record.subscription_json = serialized
        record.user_agent = user_agent.strip()
        record.updated_at = utc_now()
    else:
        record = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            subscription_json=serialized,
            user_agent=user_agent.strip(),
        )
        session.add(record)
    session.commit()
    session.refresh(record)
    return record


def unregister_push_subscription(session: Session, *, user_id: int, endpoint: str) -> bool:
    record = session.exec(
        select(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.endpoint == endpoint.strip(),
        )
    ).first()
    if not record:
        return False
    session.delete(record)
    session.commit()
    return True


def notify_users(
    session: Session,
    user_ids: Iterable[int],
    *,
    title: str,
    body: str,
    url: str = "/",
    tag: str = "rgov",
) -> int:
    ids = {user_id for user_id in user_ids if user_id}
    if not ids:
        return 0
    subscriptions = session.exec(
        select(PushSubscription).where(PushSubscription.user_id.in_(ids))
    ).all()
    return _dispatch_push_messages(
        session,
        subscriptions,
        {"title": title, "body": body, "url": url, "tag": tag},
    )


def notify_all_users(
    session: Session,
    *,
    title: str,
    body: str,
    url: str = "/",
    tag: str = "rgov",
    exclude_user_ids: Iterable[int] = (),
) -> int:
    excluded = {user_id for user_id in exclude_user_ids if user_id}
    subscriptions = session.exec(select(PushSubscription)).all()
    if excluded:
        subscriptions = [
            record for record in subscriptions if record.user_id not in excluded
        ]
    return _dispatch_push_messages(
        session,
        subscriptions,
        {"title": title, "body": body, "url": url, "tag": tag},
    )


def _serialize_subscription(subscription: dict[str, object]) -> tuple[str, str]:
    endpoint = str(subscription.get("endpoint", "")).strip()
    keys = subscription.get("keys")
    if not endpoint or not isinstance(keys, dict):
        raise ValueError("Push-подписка браузера некорректна.")
    auth = str(keys.get("auth", "")).strip()
    p256dh = str(keys.get("p256dh", "")).strip()
    if not auth or not p256dh:
        raise ValueError("Push-подписка не содержит необходимых ключей.")
    serialized = json.dumps(subscription, ensure_ascii=False, separators=(",", ":"))
    return endpoint, serialized


def _dispatch_push_messages(
    session: Session,
    subscriptions: Iterable[PushSubscription],
    payload: dict[str, str],
) -> int:
    settings = get_settings()
    if not settings.push_notifications_enabled:
        return 0

    delivered = 0
    changed = False
    stale_records: list[PushSubscription] = []
    message = json.dumps(payload, ensure_ascii=False)

    for record in subscriptions:
        try:
            webpush(
                subscription_info=json.loads(record.subscription_json),
                data=message,
                vapid_private_key=settings.push_private_key,
                vapid_claims={"sub": f"mailto:{settings.push_contact_email}"},
                ttl=3600,
            )
            record.last_success_at = utc_now()
            record.updated_at = utc_now()
            session.add(record)
            delivered += 1
            changed = True
        except WebPushException as error:
            status_code = getattr(error.response, "status_code", None)
            if status_code in {404, 410}:
                stale_records.append(record)
                changed = True
                continue
            logger.warning(
                "Failed to deliver push notification to %s: %s",
                record.endpoint,
                error,
            )
        except Exception:
            logger.exception(
                "Unexpected web push error for subscription %s",
                record.endpoint,
            )

    for record in stale_records:
        session.delete(record)

    if changed:
        session.commit()

    return delivered
