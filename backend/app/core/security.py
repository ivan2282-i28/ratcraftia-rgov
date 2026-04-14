from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlmodel import Session, select

from ..core.config import get_settings
from ..db import get_session
from ..models import User
from ..services.permissions import normalize_permissions


password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(plain_password, password_hash)


def _token_timestamps(minutes: int) -> tuple[datetime, datetime]:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=minutes)
    return issued_at, expires_at


def create_access_token(user: User) -> str:
    settings = get_settings()
    issued_at, expires_at = _token_timestamps(settings.access_token_ttl_minutes)
    payload = {
        "sub": user.uin,
        "login": user.login,
        "permissions": normalize_permissions(user.permissions),
        "iat": issued_at,
        "exp": expires_at,
        "token_type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_did_token(user: User) -> tuple[str, datetime, dict[str, str]]:
    settings = get_settings()
    issued_at, expires_at = _token_timestamps(settings.did_token_ttl_minutes)
    payload = {
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Patronymic": user.patronymic,
        "UIN": user.uin,
        "DID": "true",
        "UAN": user.uan,
        "iat": issued_at,
        "exp": expires_at,
        "token_type": "did",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    visible_payload = {
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Patronymic": user.patronymic,
        "UIN": user.uin,
        "DID": "true",
        "UAN": user.uan,
    }
    return token, expires_at, visible_payload


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк.",
        ) from error
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен.",
        ) from error


def authenticate_with_password(session: Session, identifier: str, password: str) -> User | None:
    normalized = identifier.strip()
    user = session.exec(
        select(User).where(or_(User.uin == normalized, User.login == normalized.lower()))
    ).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def authenticate_with_rgov(session: Session, login: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.login == login.strip().lower())).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def authenticate_with_uan(session: Session, uin: str, uan: str) -> User | None:
    user = session.exec(select(User).where(User.uin == uin, User.uan == uan)).first()
    if not user or not user.is_active:
        return None
    return user


def authenticate_universal(session: Session, identifier: str, secret: str) -> User | None:
    user = authenticate_with_password(session, identifier, secret)
    if user:
        return user
    return authenticate_with_uan(session, identifier.strip(), secret.strip())


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация.",
        )
    payload = decode_token(credentials.credentials)
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена.",
        )
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит идентификатора пользователя.",
        )
    user = session.exec(select(User).where(User.uin == subject)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь недоступен.",
        )
    return user
