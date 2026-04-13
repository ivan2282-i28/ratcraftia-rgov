from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..core.config import get_settings
from ..core.security import (
    authenticate_universal,
    create_external_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ..models import ExternalAuthApplication, OAuthAuthorizationCode, User, utc_now
from ..schemas import (
    ExternalAuthApplicationRead,
    ExternalAuthApplicationRequest,
    ExternalAuthApplicationSecretResponse,
    ExternalAuthApplicationStatusResponse,
    ExternalAuthProfileResponse,
    OAuthTokenResponse,
)
from .permissions import EXTERNAL_APPS_APPROVE_PERMISSION, require_permission
from .portal import (
    _record_admin_log,
    full_name,
    get_org,
    serialize_org,
    touch,
)


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _generate_client_id() -> str:
    return f"rgovapp_{secrets.token_hex(12)}"


def _generate_client_secret() -> str:
    return secrets.token_urlsafe(32)


def _hash_authorization_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def append_query_params(url: str, params: dict[str, str]) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: value for key, value in params.items() if value != ""})
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )


def build_oauth_error_redirect(
    redirect_uri: str,
    *,
    error: str,
    state: str = "",
    error_description: str = "",
) -> str:
    return append_query_params(
        redirect_uri,
        {
            "error": error,
            "error_description": error_description,
            "state": state,
        },
    )


def _find_by_client_id(
    session: Session,
    client_id: str,
) -> ExternalAuthApplication | None:
    return session.exec(
        select(ExternalAuthApplication).where(
            ExternalAuthApplication.client_id == client_id.strip()
        )
    ).first()


def serialize_external_auth_application(
    session: Session,
    application: ExternalAuthApplication,
) -> ExternalAuthApplicationRead:
    approver = (
        session.get(User, application.approved_by_id)
        if application.approved_by_id
        else None
    )
    return ExternalAuthApplicationRead(
        id=application.id,
        name=application.name,
        description=application.description,
        homepage_url=application.homepage_url,
        contact_email=application.contact_email,
        redirect_uri=application.redirect_uri,
        client_id=application.client_id,
        is_approved=application.is_approved,
        approved_at=application.approved_at,
        approved_by_name=full_name(approver) if approver else None,
        is_active=application.is_active,
        last_token_issued_at=application.last_token_issued_at,
    )


def serialize_external_auth_profile(
    session: Session,
    user: User,
) -> ExternalAuthProfileResponse:
    org = get_org(session, user)
    return ExternalAuthProfileResponse(
        id=user.id,
        uin=user.uin,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        full_name=full_name(user),
        organization=serialize_org(org) if org else None,
        photo_url=user.photo_url,
    )


def create_external_auth_application(
    session: Session,
    payload: ExternalAuthApplicationRequest,
) -> ExternalAuthApplicationSecretResponse:
    client_id = _generate_client_id()
    while _find_by_client_id(session, client_id):
        client_id = _generate_client_id()
    client_secret = _generate_client_secret()

    application = ExternalAuthApplication(
        name=payload.name.strip(),
        description=payload.description.strip(),
        homepage_url=payload.homepage_url.strip(),
        contact_email=payload.contact_email.strip(),
        redirect_uri=payload.redirect_uri.strip(),
        client_id=client_id,
        client_secret_hash=get_password_hash(client_secret),
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return ExternalAuthApplicationSecretResponse(
        application=serialize_external_auth_application(session, application),
        client_secret=client_secret,
    )


def get_external_auth_application_or_404(
    session: Session,
    app_id: int,
) -> ExternalAuthApplication:
    application = session.get(ExternalAuthApplication, app_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Внешнее приложение не найдено.",
        )
    return application


def get_external_auth_application_status(
    session: Session,
    client_id: str,
) -> ExternalAuthApplicationStatusResponse:
    application = _find_by_client_id(session, client_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Внешнее приложение не найдено.",
        )
    return ExternalAuthApplicationStatusResponse(
        client_id=application.client_id,
        is_approved=application.is_approved,
        is_active=application.is_active,
    )


def list_external_auth_applications(
    session: Session,
) -> list[ExternalAuthApplicationRead]:
    applications = session.exec(
        select(ExternalAuthApplication).order_by(
            ExternalAuthApplication.created_at.desc()
        )
    ).all()
    return [
        serialize_external_auth_application(session, application)
        for application in applications
    ]


def approve_external_auth_application(
    session: Session,
    actor: User,
    application: ExternalAuthApplication,
) -> ExternalAuthApplicationRead:
    require_permission(actor, EXTERNAL_APPS_APPROVE_PERMISSION)
    application.is_approved = True
    application.is_active = True
    application.approved_at = utc_now()
    application.approved_by_id = actor.id
    touch(application)
    session.add(application)
    _record_admin_log(
        session,
        actor,
        action="external_auth.approve",
        summary=f"Одобрено внешнее приложение {application.name}",
        target_label=application.client_id,
    )
    session.commit()
    session.refresh(application)
    return serialize_external_auth_application(session, application)


def deactivate_external_auth_application(
    session: Session,
    actor: User,
    application: ExternalAuthApplication,
) -> ExternalAuthApplicationRead:
    require_permission(actor, EXTERNAL_APPS_APPROVE_PERMISSION)
    application.is_active = False
    touch(application)
    session.add(application)
    _record_admin_log(
        session,
        actor,
        action="external_auth.deactivate",
        summary=f"Отключено внешнее приложение {application.name}",
        target_label=application.client_id,
    )
    session.commit()
    session.refresh(application)
    return serialize_external_auth_application(session, application)


def validate_oauth_application(
    session: Session,
    client_id: str,
    redirect_uri: str,
) -> ExternalAuthApplication:
    application = _find_by_client_id(session, client_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неизвестный client_id.",
        )
    if application.redirect_uri.strip() != redirect_uri.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="redirect_uri не совпадает с зарегистрированным адресом.",
        )
    return application


def authenticate_user_for_oauth(
    session: Session,
    identifier: str,
    secret: str,
) -> User:
    user = authenticate_universal(session, identifier, secret)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные пользователя RGOV.",
        )
    return user


def issue_authorization_code(
    session: Session,
    application: ExternalAuthApplication,
    user: User,
    redirect_uri: str,
) -> str:
    expires_at = utc_now() + timedelta(minutes=get_settings().oauth_code_ttl_minutes)
    raw_code = secrets.token_urlsafe(32)
    code_hash = _hash_authorization_code(raw_code)
    while session.exec(
        select(OAuthAuthorizationCode).where(
            OAuthAuthorizationCode.code_hash == code_hash
        )
    ).first():
        raw_code = secrets.token_urlsafe(32)
        code_hash = _hash_authorization_code(raw_code)

    session.add(
        OAuthAuthorizationCode(
            application_id=application.id,
            user_id=user.id,
            code_hash=code_hash,
            redirect_uri=redirect_uri.strip(),
            expires_at=expires_at,
        )
    )
    session.commit()
    return raw_code


def _authenticate_external_application(
    session: Session,
    client_id: str,
    client_secret: str,
) -> ExternalAuthApplication:
    application = _find_by_client_id(session, client_id)
    if not application or not verify_password(
        client_secret,
        application.client_secret_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные client_id или client_secret.",
        )
    if application.redirect_uri.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У приложения не настроен redirect_uri.",
        )
    if not application.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приложение ещё не одобрено администратором.",
        )
    if not application.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Внешнее приложение отключено.",
        )
    return application


def exchange_authorization_code(
    session: Session,
    *,
    grant_type: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
) -> OAuthTokenResponse:
    if grant_type.strip() != "authorization_code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поддерживается только grant_type=authorization_code.",
        )
    application = _authenticate_external_application(session, client_id, client_secret)
    normalized_redirect_uri = redirect_uri.strip()
    if application.redirect_uri.strip() != normalized_redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="redirect_uri не совпадает с зарегистрированным адресом.",
        )

    record = session.exec(
        select(OAuthAuthorizationCode).where(
            OAuthAuthorizationCode.application_id == application.id,
            OAuthAuthorizationCode.code_hash == _hash_authorization_code(code.strip()),
            OAuthAuthorizationCode.redirect_uri == normalized_redirect_uri,
        )
    ).first()
    if not record or record.used_at is not None or _as_utc(record.expires_at) < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код авторизации недействителен или истёк.",
        )

    record.used_at = utc_now()
    touch(record)
    application.last_token_issued_at = utc_now()
    touch(application)
    session.add(record)
    session.add(application)
    session.commit()

    user = session.get(User, record.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь недоступен.",
        )
    token, _ = create_external_access_token(user, application)
    return OAuthTokenResponse(
        access_token=token,
        expires_in=get_settings().access_token_ttl_minutes * 60,
    )


def get_external_auth_context(
    session: Session,
    token: str,
) -> tuple[User, ExternalAuthApplication]:
    payload = decode_token(token)
    if payload.get("token_type") != "external_access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип внешнего токена.",
        )
    subject = str(payload.get("sub", "")).strip()
    app_client_id = str(payload.get("app_client_id", "")).strip()
    if not subject or not app_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен внешней авторизации повреждён.",
        )
    user = session.exec(select(User).where(User.uin == subject)).first()
    application = _find_by_client_id(session, app_client_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь недоступен.",
        )
    if not application or not application.is_approved or not application.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Внешнее приложение недоступно.",
        )
    return user, application
