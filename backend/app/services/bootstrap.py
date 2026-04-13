from __future__ import annotations

from sqlmodel import Session, select

from ..core.security import get_password_hash
from ..models import User
from .permissions import serialize_permissions


def _ensure_user(
    session: Session,
    *,
    uin: str,
    uan: str,
    login: str,
    first_name: str,
    last_name: str,
    patronymic: str,
    password: str,
    permissions: list[str],
    org_id: int | None,
    position_title: str,
) -> User:
    user = session.exec(select(User).where(User.login == login)).first()
    permissions_value = serialize_permissions(permissions)
    if user:
        if user.permissions != permissions_value:
            user.permissions = permissions_value
            session.add(user)
            session.flush()
        return user
    user = User(
        uin=uin,
        uan=uan,
        login=login,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        password_hash=get_password_hash(password),
        permissions=permissions_value,
        org_id=org_id,
        position_title=position_title,
    )
    session.add(user)
    session.flush()
    return user


def seed_demo_data(session: Session) -> None:
    _ensure_user(
        session,
        uin="ROOT",
        uan="RGOV-ROOT-001",
        login="root",
        first_name="ROOT",
        last_name="RGOV",
        patronymic="",
        password="RGOV-DEFAULT_ROOT",
        permissions=["*"],
        org_id=None,
        position_title="Системный аккаунт RGOV",
    )
    session.commit()
