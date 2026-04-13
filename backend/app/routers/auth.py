from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.security import (
    authenticate_universal,
    authenticate_with_password,
    authenticate_with_rgov,
    authenticate_with_uan,
    create_access_token,
    get_current_user,
)
from ..db import get_session
from ..models import User
from ..schemas import (
    AuthLoginRequest,
    LoginChangeRequest,
    MessageResponse,
    PasswordChangeRequest,
    PasswordLoginRequest,
    ProfileResponse,
    RgovLoginRequest,
    TokenResponse,
    UanLoginRequest,
)
from ..services.portal import change_login, change_password, serialize_profile


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthLoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_universal(session, payload.identifier, payload.secret)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные.",
        )
    return TokenResponse(access_token=create_access_token(user), profile=serialize_profile(session, user))


@router.post("/login/password", response_model=TokenResponse)
def login_with_password(payload: PasswordLoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_with_password(session, payload.identifier.strip(), payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные.",
        )
    return TokenResponse(access_token=create_access_token(user), profile=serialize_profile(session, user))


@router.post("/login/uan", response_model=TokenResponse)
def login_with_uan(payload: UanLoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_with_uan(session, payload.uin.strip(), payload.uan.strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные УИН или УАН.",
        )
    return TokenResponse(access_token=create_access_token(user), profile=serialize_profile(session, user))


@router.post("/login/rgov", response_model=TokenResponse)
def login_with_rgov(payload: RgovLoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_with_rgov(session, payload.login, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный RGOV-логин или пароль.",
        )
    return TokenResponse(access_token=create_access_token(user), profile=serialize_profile(session, user))


@router.get("/me", response_model=ProfileResponse)
def get_me(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    return serialize_profile(session, user)


@router.post("/change-login", response_model=ProfileResponse)
def update_login(
    payload: LoginChangeRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProfileResponse:
    try:
        return change_login(session, user, payload.new_login)
    except (PermissionError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/change-password", response_model=MessageResponse)
def update_password(
    payload: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MessageResponse:
    try:
        change_password(session, user, payload)
    except (PermissionError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return MessageResponse(detail="Пароль обновлён.")
