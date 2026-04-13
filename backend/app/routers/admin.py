from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.security import get_current_user
from ..db import get_session
from ..models import Organization, User
from ..schemas import (
    AdminLogRead,
    ExternalAuthApplicationRead,
    HireRequest,
    OrganizationCreate,
    OrganizationRead,
    PermissionChangeRequest,
    UserCreate,
    UserRead,
    UserUpdate,
)
from ..services.permissions import (
    ADMIN_LOGS_READ_PERMISSION,
    EXTERNAL_APPS_READ_PERMISSION,
    ORGS_CREATE_PERMISSION,
    ORGS_READ_PERMISSION,
    USERS_CREATE_PERMISSION,
    USERS_READ_PERMISSION,
    has_permission,
)
from ..services.external_auth import (
    approve_external_auth_application,
    deactivate_external_auth_application,
    get_external_auth_application_or_404,
    list_external_auth_applications,
)
from ..services.portal import (
    change_user_permissions,
    create_org,
    create_user,
    fire_user,
    hire_user,
    list_admin_logs,
    serialize_org,
    serialize_user,
    update_user_identity,
)


router = APIRouter(prefix="/api/admin", tags=["admin"])


def _get_target_user(session: Session, user_id: int) -> User:
    target = session.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")
    return target


def _ensure_admin_or_executive(actor: User) -> None:
    if not has_permission(actor, USERS_READ_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра пользователей.",
        )


@router.get("/users", response_model=list[UserRead])
def list_users(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[UserRead]:
    _ensure_admin_or_executive(user)
    users = session.exec(select(User).order_by(User.last_name, User.first_name)).all()
    return [serialize_user(session, user, show_uan=True) for user in users]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def add_user(
    payload: UserCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    if not has_permission(user, USERS_CREATE_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания пользователей.",
        )
    try:
        return create_user(session, payload, actor=user)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    try:
        return update_user_identity(session, user, _get_target_user(session, user_id), payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/users/{user_id}/permissions", response_model=UserRead)
def update_permissions(
    user_id: int,
    payload: PermissionChangeRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    try:
        return change_user_permissions(
            session,
            user,
            _get_target_user(session, user_id),
            payload.permissions,
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.post("/users/{user_id}/hire", response_model=UserRead)
def assign_user(
    user_id: int,
    payload: HireRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    try:
        return hire_user(session, user, _get_target_user(session, user_id), payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/users/{user_id}/fire", response_model=UserRead)
def dismiss_user(
    user_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    try:
        return fire_user(session, user, _get_target_user(session, user_id))
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.get("/organizations", response_model=list[OrganizationRead])
def list_orgs(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[OrganizationRead]:
    if not has_permission(user, ORGS_READ_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра организаций.",
        )
    orgs = session.exec(select(Organization).order_by(Organization.name)).all()
    return [serialize_org(org) for org in orgs]


@router.post("/organizations", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def add_org(
    payload: OrganizationCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> OrganizationRead:
    if not has_permission(user, ORGS_CREATE_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания организаций.",
        )
    try:
        return create_org(session, user, payload)
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/logs", response_model=list[AdminLogRead])
def get_admin_logs(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[AdminLogRead]:
    if not has_permission(user, ADMIN_LOGS_READ_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра журналов.",
        )
    return list_admin_logs(session, user)


@router.get("/external-auth-apps", response_model=list[ExternalAuthApplicationRead])
def get_external_auth_apps(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[ExternalAuthApplicationRead]:
    if not has_permission(user, EXTERNAL_APPS_READ_PERMISSION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра внешних приложений.",
        )
    return list_external_auth_applications(session)


@router.post("/external-auth-apps/{app_id}/approve", response_model=ExternalAuthApplicationRead)
def approve_external_auth_app(
    app_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ExternalAuthApplicationRead:
    try:
        return approve_external_auth_application(
            session,
            user,
            get_external_auth_application_or_404(session, app_id),
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.post("/external-auth-apps/{app_id}/deactivate", response_model=ExternalAuthApplicationRead)
def deactivate_external_auth_app(
    app_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ExternalAuthApplicationRead:
    try:
        return deactivate_external_auth_application(
            session,
            user,
            get_external_auth_application_or_404(session, app_id),
        )
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
