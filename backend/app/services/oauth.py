from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import json
import re
import secrets
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select

from ..core.security import (
    bearer_scheme,
    create_oauth_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ..db import get_session
from ..models import AdminLog, OAuthAccessToken, OAuthApplication, OAuthAuthorizationCode, User, utc_now
from ..schemas import (
    DeveloperAppCreate,
    DeveloperAppCreateResponse,
    DeveloperAppRead,
    DeveloperAppReviewRequest,
    DeveloperAppSecretResponse,
    OAuthAuthorizationRequest,
    OAuthAuthorizationResponse,
    OAuthTokenResponse,
    OAuthUserInfoResponse,
    PublicOAuthAppRead,
)
from .permissions import (
    OAUTH_APPS_READ_PERMISSION,
    OAUTH_APPS_REVIEW_PERMISSION,
    has_permission,
    normalize_permissions,
    require_permission,
)
from .portal import full_name, get_org


OAUTH_SCOPE_PROFILE_BASIC = "profile.basic"
OAUTH_SCOPE_PROFILE_ORGANIZATION = "profile.organization"
OAUTH_SCOPE_PROFILE_PERMISSIONS = "profile.permissions"

OAUTH_SCOPE_DESCRIPTIONS = {
    OAUTH_SCOPE_PROFILE_BASIC: "Basic RGOV identity fields.",
    OAUTH_SCOPE_PROFILE_ORGANIZATION: "Organization and current position data.",
    OAUTH_SCOPE_PROFILE_PERMISSIONS: "RGOV permission grants assigned to the citizen.",
}

OAUTH_APP_STATUSES = {"pending", "approved", "rejected", "revoked"}
_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class OAuthIdentity:
    user: User
    application: OAuthApplication
    token: OAuthAccessToken
    scopes: list[str]


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=utc_now().tzinfo)
    return value.astimezone(utc_now().tzinfo)


def normalize_oauth_scopes(raw: list[str] | str | None) -> list[str]:
    if raw is None:
        return [OAUTH_SCOPE_PROFILE_BASIC]
    if isinstance(raw, str):
        items = raw.replace(",", " ").split()
    else:
        items = raw
    normalized: list[str] = []
    for item in items:
        scope = str(item).strip().lower()
        if not scope:
            continue
        if scope not in OAUTH_SCOPE_DESCRIPTIONS:
            raise ValueError(f"Неизвестный OAuth scope: {scope}")
        if scope not in normalized:
            normalized.append(scope)
    return normalized or [OAUTH_SCOPE_PROFILE_BASIC]


def serialize_oauth_scopes(raw: list[str] | str | None) -> str:
    return " ".join(normalize_oauth_scopes(raw))


def oauth_scope_catalog() -> list[dict[str, str]]:
    return [
        {"scope": scope, "description": description}
        for scope, description in OAUTH_SCOPE_DESCRIPTIONS.items()
    ]


def _normalize_slug(value: str) -> str:
    slug = value.strip().lower()
    if not _SLUG_PATTERN.match(slug):
        raise ValueError("Slug может содержать только латиницу, цифры и дефисы.")
    return slug


def _validate_url(value: str, *, label: str) -> str:
    candidate = value.strip()
    if not candidate:
        return ""
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{label} должен использовать http:// или https://")
    return candidate


def normalize_redirect_uris(values: list[str] | str) -> list[str]:
    raw_values = values
    if isinstance(values, str):
        raw_values = [item for item in re.split(r"[\n,]+", values) if item.strip()]
    redirect_uris: list[str] = []
    for item in raw_values:
        uri = _validate_url(str(item), label="Redirect URI")
        if uri and uri not in redirect_uris:
            redirect_uris.append(uri)
    if not redirect_uris:
        raise ValueError("Нужен хотя бы один redirect URI.")
    return redirect_uris


def serialize_redirect_uris(values: list[str] | str) -> str:
    return json.dumps(normalize_redirect_uris(values), ensure_ascii=False)


def parse_redirect_uris(raw: str | None) -> list[str]:
    if not raw:
        return []
    data = json.loads(raw)
    return normalize_redirect_uris(data)


def _owner_name(session: Session, application: OAuthApplication) -> str:
    owner = session.get(User, application.owner_user_id)
    return full_name(owner) if owner else "Неизвестный владелец"


def serialize_developer_app(session: Session, application: OAuthApplication) -> DeveloperAppRead:
    return DeveloperAppRead(
        id=application.id,
        name=application.name,
        slug=application.slug,
        description=application.description,
        website_url=application.website_url,
        redirect_uris=parse_redirect_uris(application.redirect_uris_json),
        allowed_scopes=normalize_oauth_scopes(application.allowed_scopes),
        client_id=application.client_id,
        status=application.status,
        review_note=application.review_note,
        owner_name=_owner_name(session, application),
        approved_at=application.approved_at,
        created_at=application.created_at,
        updated_at=application.updated_at,
        last_secret_rotated_at=application.last_secret_rotated_at,
    )


def serialize_public_oauth_app(session: Session, application: OAuthApplication) -> PublicOAuthAppRead:
    return PublicOAuthAppRead(
        client_id=application.client_id,
        name=application.name,
        description=application.description,
        website_url=application.website_url,
        status=application.status,
        owner_name=_owner_name(session, application),
        allowed_scopes=normalize_oauth_scopes(application.allowed_scopes),
    )


def _build_redirect_uri(base_uri: str, **params: str) -> str:
    parsed = urlparse(base_uri)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for key, value in params.items():
        if value:
            query[key] = value
    return urlunparse(parsed._replace(query=urlencode(query)))


def _generate_unique_value(session: Session, *, field: str, prefix: str) -> str:
    model_field = getattr(OAuthApplication, field)
    while True:
        candidate = f"{prefix}{secrets.token_urlsafe(24)}".replace("-", "").replace("_", "")
        existing = session.exec(select(OAuthApplication).where(model_field == candidate)).first()
        if not existing:
            return candidate


def _get_application_by_id(session: Session, app_id: int) -> OAuthApplication:
    application = session.get(OAuthApplication, app_id)
    if not application:
        raise ValueError("OAuth-приложение не найдено.")
    return application


def _get_application_by_client_id(session: Session, client_id: str) -> OAuthApplication:
    application = session.exec(
        select(OAuthApplication).where(OAuthApplication.client_id == client_id.strip())
    ).first()
    if not application:
        raise ValueError("OAuth-приложение не найдено.")
    return application


def _validate_authorization_request(
    session: Session,
    payload: OAuthAuthorizationRequest,
    *,
    require_approved: bool,
) -> tuple[OAuthApplication, list[str], str]:
    application = _get_application_by_client_id(session, payload.client_id)
    if payload.response_type != "code":
        raise ValueError("Поддерживается только response_type=code.")

    redirect_uri = payload.redirect_uri.strip()
    if redirect_uri not in parse_redirect_uris(application.redirect_uris_json):
        raise ValueError("Redirect URI не зарегистрирован для этого приложения.")

    requested_scopes = normalize_oauth_scopes(payload.scope)
    allowed_scopes = set(normalize_oauth_scopes(application.allowed_scopes))
    if not set(requested_scopes).issubset(allowed_scopes):
        raise ValueError("Приложение запросило scope, который не был зарегистрирован.")

    if require_approved and application.status != "approved":
        raise PermissionError("Приложение ещё не одобрено администратором RGOV.")

    return application, requested_scopes, redirect_uri


def list_developer_apps(session: Session, actor: User) -> list[DeveloperAppRead]:
    applications = session.exec(
        select(OAuthApplication)
        .where(OAuthApplication.owner_user_id == actor.id)
        .order_by(OAuthApplication.created_at.desc())
    ).all()
    return [serialize_developer_app(session, application) for application in applications]


def register_developer_app(
    session: Session,
    actor: User,
    payload: DeveloperAppCreate,
) -> DeveloperAppCreateResponse:
    slug = _normalize_slug(payload.slug)
    if session.exec(select(OAuthApplication).where(OAuthApplication.slug == slug)).first():
        raise ValueError("Приложение с таким slug уже существует.")

    website_url = _validate_url(payload.website_url, label="Website URL") if payload.website_url else ""
    redirect_uris_json = serialize_redirect_uris(payload.redirect_uris)
    allowed_scopes = serialize_oauth_scopes(payload.allowed_scopes)
    client_id = _generate_unique_value(session, field="client_id", prefix="rgov_")
    client_secret = secrets.token_urlsafe(32)

    application = OAuthApplication(
        owner_user_id=actor.id,
        name=payload.name.strip(),
        slug=slug,
        description=payload.description.strip(),
        website_url=website_url,
        redirect_uris_json=redirect_uris_json,
        allowed_scopes=allowed_scopes,
        client_id=client_id,
        client_secret_hash=get_password_hash(client_secret),
        status="pending",
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return DeveloperAppCreateResponse(
        **serialize_developer_app(session, application).model_dump(),
        client_secret=client_secret,
    )


def rotate_developer_app_secret(
    session: Session,
    actor: User,
    app_id: int,
) -> DeveloperAppSecretResponse:
    application = _get_application_by_id(session, app_id)
    if application.owner_user_id != actor.id and not has_permission(actor, OAUTH_APPS_REVIEW_PERMISSION):
        raise PermissionError("Нельзя менять секрет чужого приложения.")

    client_secret = secrets.token_urlsafe(32)
    rotated_at = utc_now()
    application.client_secret_hash = get_password_hash(client_secret)
    application.last_secret_rotated_at = rotated_at
    application.updated_at = rotated_at
    session.add(application)
    session.commit()
    return DeveloperAppSecretResponse(
        client_id=application.client_id,
        client_secret=client_secret,
        rotated_at=rotated_at,
    )


def list_all_oauth_apps(session: Session, actor: User) -> list[DeveloperAppRead]:
    require_permission(actor, OAUTH_APPS_READ_PERMISSION)
    applications = session.exec(
        select(OAuthApplication).order_by(OAuthApplication.created_at.desc())
    ).all()
    return [serialize_developer_app(session, application) for application in applications]


def review_oauth_app(
    session: Session,
    actor: User,
    app_id: int,
    payload: DeveloperAppReviewRequest,
) -> DeveloperAppRead:
    require_permission(actor, OAUTH_APPS_REVIEW_PERMISSION)
    application = _get_application_by_id(session, app_id)

    status_value = payload.status.strip().lower()
    if status_value not in OAUTH_APP_STATUSES - {"pending"}:
        raise ValueError("Недопустимый статус OAuth-приложения.")

    now = utc_now()
    application.status = status_value
    application.review_note = payload.review_note.strip()
    application.approved_by_user_id = actor.id
    application.updated_at = now
    if status_value == "approved":
        application.approved_at = now
    elif status_value == "rejected":
        application.approved_at = None

    session.add(application)
    session.add(
        AdminLog(
            actor_id=actor.id,
            action="oauth.app.review",
            summary=f"OAuth-приложение {application.name} переведено в статус {status_value}",
            target_label=application.name,
            reason=application.review_note,
        )
    )
    session.commit()
    session.refresh(application)
    return serialize_developer_app(session, application)


def get_public_oauth_app(session: Session, client_id: str) -> PublicOAuthAppRead:
    return serialize_public_oauth_app(session, _get_application_by_client_id(session, client_id))


def build_frontend_authorize_path(payload: OAuthAuthorizationRequest) -> str:
    params = {
        "client_id": payload.client_id.strip(),
        "redirect_uri": payload.redirect_uri.strip(),
        "response_type": payload.response_type.strip(),
        "scope": serialize_oauth_scopes(payload.scope),
    }
    if payload.state:
        params["state"] = payload.state
    return f"/oauth/authorize?{urlencode(params)}"


def authorize_oauth_application(
    session: Session,
    actor: User,
    payload: OAuthAuthorizationRequest,
) -> OAuthAuthorizationResponse:
    application, scopes, redirect_uri = _validate_authorization_request(
        session,
        payload,
        require_approved=True,
    )

    code = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(minutes=10)
    session.add(
        OAuthAuthorizationCode(
            application_id=application.id,
            user_id=actor.id,
            code=code,
            redirect_uri=redirect_uri,
            scopes=serialize_oauth_scopes(scopes),
            expires_at=expires_at,
        )
    )
    session.commit()
    return OAuthAuthorizationResponse(
        redirect_to=_build_redirect_uri(redirect_uri, code=code, state=payload.state or ""),
        expires_at=expires_at,
    )


def deny_oauth_application(
    session: Session,
    payload: OAuthAuthorizationRequest,
) -> OAuthAuthorizationResponse:
    _, _, redirect_uri = _validate_authorization_request(
        session,
        payload,
        require_approved=False,
    )
    return OAuthAuthorizationResponse(
        redirect_to=_build_redirect_uri(
            redirect_uri,
            error="access_denied",
            error_description="The RGOV user denied access.",
            state=payload.state or "",
        )
    )


def exchange_oauth_authorization_code(
    session: Session,
    *,
    grant_type: str,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
) -> OAuthTokenResponse:
    if grant_type != "authorization_code":
        raise ValueError("Поддерживается только grant_type=authorization_code.")

    application = _get_application_by_client_id(session, client_id)
    if application.status != "approved":
        raise PermissionError("Приложение не одобрено для OAuth-доступа.")
    if not verify_password(client_secret, application.client_secret_hash):
        raise PermissionError("Неверный client_secret.")

    auth_code = session.exec(
        select(OAuthAuthorizationCode).where(OAuthAuthorizationCode.code == code.strip())
    ).first()
    if not auth_code or auth_code.application_id != application.id:
        raise ValueError("Authorization code недействителен.")
    if auth_code.redirect_uri != redirect_uri.strip():
        raise ValueError("redirect_uri не совпадает с кодом авторизации.")
    if auth_code.used_at is not None:
        raise ValueError("Authorization code уже был использован.")
    if _as_utc(auth_code.expires_at) < utc_now():
        raise ValueError("Срок действия authorization code истёк.")

    user = session.get(User, auth_code.user_id)
    if not user or not user.is_active:
        raise PermissionError("Пользователь больше недоступен.")

    token_id = secrets.token_urlsafe(24)
    scopes = normalize_oauth_scopes(auth_code.scopes)
    access_token, expires_at = create_oauth_access_token(
        user,
        client_id=application.client_id,
        scopes=scopes,
        token_id=token_id,
    )

    auth_code.used_at = utc_now()
    session.add(auth_code)
    session.add(
        OAuthAccessToken(
            application_id=application.id,
            user_id=user.id,
            token_id=token_id,
            scopes=serialize_oauth_scopes(scopes),
            expires_at=expires_at,
        )
    )
    session.commit()
    return OAuthTokenResponse(
        access_token=access_token,
        expires_in=max(1, int((expires_at - utc_now()).total_seconds())),
        scope=serialize_oauth_scopes(scopes),
    )


def _oauth_http_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def get_current_oauth_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> OAuthIdentity:
    if credentials is None:
        raise _oauth_http_error("OAuth bearer token is required.")

    payload = decode_token(credentials.credentials)
    if payload.get("token_type") != "oauth_access":
        raise _oauth_http_error("Invalid token type for the public API.")

    token_id = str(payload.get("jti") or "").strip()
    client_id = str(payload.get("client_id") or "").strip()
    if not token_id or not client_id:
        raise _oauth_http_error("OAuth token payload is incomplete.")

    access_token = session.exec(
        select(OAuthAccessToken).where(OAuthAccessToken.token_id == token_id)
    ).first()
    if (
        not access_token
        or access_token.revoked_at is not None
        or _as_utc(access_token.expires_at) < utc_now()
    ):
        raise _oauth_http_error("OAuth token is no longer active.")

    application = session.get(OAuthApplication, access_token.application_id)
    if not application or application.client_id != client_id or application.status != "approved":
        raise _oauth_http_error("OAuth application is no longer available.")

    user = session.get(User, access_token.user_id)
    if not user or not user.is_active:
        raise _oauth_http_error("OAuth subject is no longer available.")

    return OAuthIdentity(
        user=user,
        application=application,
        token=access_token,
        scopes=normalize_oauth_scopes(payload.get("scope") or access_token.scopes),
    )


def serialize_oauth_userinfo(session: Session, identity: OAuthIdentity) -> OAuthUserInfoResponse:
    organization = get_org(session, identity.user)
    permissions: list[str] | None = None
    if OAUTH_SCOPE_PROFILE_PERMISSIONS in identity.scopes:
        permissions = normalize_permissions(identity.user.permissions)

    return OAuthUserInfoResponse(
        sub=identity.user.uin,
        client_id=identity.application.client_id,
        scopes=identity.scopes,
        uin=identity.user.uin,
        login=identity.user.login,
        first_name=identity.user.first_name,
        last_name=identity.user.last_name,
        patronymic=identity.user.patronymic,
        full_name=full_name(identity.user),
        organization_slug=organization.slug if organization and OAUTH_SCOPE_PROFILE_ORGANIZATION in identity.scopes else None,
        organization_name=organization.name if organization and OAUTH_SCOPE_PROFILE_ORGANIZATION in identity.scopes else None,
        position_title=identity.user.position_title if OAUTH_SCOPE_PROFILE_ORGANIZATION in identity.scopes else None,
        permissions=permissions,
    )
