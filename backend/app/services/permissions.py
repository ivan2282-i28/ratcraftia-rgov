from __future__ import annotations

from collections.abc import Iterable
from typing import Any


ROOT_LOGIN = "root"
WILDCARD_PERMISSION = "*"

USERS_READ_PERMISSION = "admin.users.read"
USERS_CREATE_PERMISSION = "admin.users.create"
USERS_UPDATE_PERMISSION = "admin.users.update"
USER_PERMISSIONS_WRITE_PERMISSION = "admin.users.permissions.write"
ORGS_READ_PERMISSION = "admin.organizations.read"
ORGS_CREATE_PERMISSION = "admin.organizations.create"
PERSONNEL_MANAGE_PERMISSION = "admin.personnel.manage"
ADMIN_LOGS_READ_PERMISSION = "admin.logs.read"
OAUTH_APPS_READ_PERMISSION = "admin.oauth_apps.read"
OAUTH_APPS_REVIEW_PERMISSION = "admin.oauth_apps.review"
NEWS_MANAGE_PERMISSION = "news.manage"
BILLS_MANAGE_PERMISSION = "bills.manage"
REFERENDA_MANAGE_PERMISSION = "referenda.manage"
RATUBLES_MINT_PERMISSION = "ratubles.mint"

PRESET_PERMISSIONS = {
    "citizen": [],
    "government_staff": [
        NEWS_MANAGE_PERMISSION,
    ],
    "executive_officer": [
        NEWS_MANAGE_PERMISSION,
        ORGS_CREATE_PERMISSION,
        ORGS_READ_PERMISSION,
        PERSONNEL_MANAGE_PERMISSION,
        REFERENDA_MANAGE_PERMISSION,
        USERS_READ_PERMISSION,
    ],
    "parliament_member": [
        BILLS_MANAGE_PERMISSION,
        REFERENDA_MANAGE_PERMISSION,
    ],
    "admin": [
        ADMIN_LOGS_READ_PERMISSION,
        BILLS_MANAGE_PERMISSION,
        NEWS_MANAGE_PERMISSION,
        ORGS_CREATE_PERMISSION,
        ORGS_READ_PERMISSION,
        OAUTH_APPS_READ_PERMISSION,
        OAUTH_APPS_REVIEW_PERMISSION,
        PERSONNEL_MANAGE_PERMISSION,
        REFERENDA_MANAGE_PERMISSION,
        RATUBLES_MINT_PERMISSION,
        USERS_CREATE_PERMISSION,
        USERS_READ_PERMISSION,
        USERS_UPDATE_PERMISSION,
        USER_PERMISSIONS_WRITE_PERMISSION,
    ],
}

PRESET_LABELS = {
    frozenset(): "Базовый доступ",
    frozenset(PRESET_PERMISSIONS["government_staff"]): "Управление новостями",
    frozenset(PRESET_PERMISSIONS["executive_officer"]): "Исполнительный доступ",
    frozenset(PRESET_PERMISSIONS["parliament_member"]): "Парламентский доступ",
    frozenset(PRESET_PERMISSIONS["admin"]): "Административный доступ",
    frozenset({WILDCARD_PERMISSION}): "Полный доступ",
}

PERMISSION_LABELS = {
    USERS_READ_PERMISSION: "Просмотр пользователей",
    USERS_CREATE_PERMISSION: "Создание пользователей",
    USERS_UPDATE_PERMISSION: "Редактирование пользователей",
    USER_PERMISSIONS_WRITE_PERMISSION: "Изменение прав доступа",
    ORGS_READ_PERMISSION: "Просмотр организаций",
    ORGS_CREATE_PERMISSION: "Создание организаций",
    PERSONNEL_MANAGE_PERMISSION: "Кадровые операции",
    ADMIN_LOGS_READ_PERMISSION: "Просмотр журналов администратора",
    OAUTH_APPS_READ_PERMISSION: "Просмотр OAuth-приложений",
    OAUTH_APPS_REVIEW_PERMISSION: "Одобрение OAuth-приложений",
    NEWS_MANAGE_PERMISSION: "Управление новостями",
    BILLS_MANAGE_PERMISSION: "Парламентские операции",
    REFERENDA_MANAGE_PERMISSION: "Референдумы",
    RATUBLES_MINT_PERMISSION: "Эмиссия Ratubles",
    WILDCARD_PERMISSION: "Полный доступ",
}


def normalize_permissions(raw: Iterable[str] | str | None) -> list[str]:
    if raw is None:
        return []
    items = raw.split(",") if isinstance(raw, str) else raw
    normalized: set[str] = set()
    for item in items:
        value = str(item).strip().lower()
        if not value:
            continue
        if value == WILDCARD_PERMISSION:
            return [WILDCARD_PERMISSION]
        normalized.add(value)
    return sorted(normalized)


def serialize_permissions(raw: Iterable[str] | str | None) -> str:
    return ",".join(normalize_permissions(raw))


def permissions_label(raw: Iterable[str] | str | None) -> str:
    normalized = normalize_permissions(raw)
    preset_label = PRESET_LABELS.get(frozenset(normalized))
    if preset_label:
        return preset_label
    if not normalized:
        return "Базовый доступ"
    return ", ".join(PERMISSION_LABELS.get(item, item) for item in normalized)


def permissions_from_legacy_role(role: str | None, *, login: str | None = None) -> list[str]:
    if (login or "").strip().lower() == ROOT_LOGIN:
        return [WILDCARD_PERMISSION]
    return PRESET_PERMISSIONS.get((role or "").strip().lower(), [])


def has_permission(actor: Any, permission: str) -> bool:
    permissions = normalize_permissions(getattr(actor, "permissions", actor))
    return WILDCARD_PERMISSION in permissions or permission in permissions


def require_permission(
    actor: Any,
    permission: str,
    *,
    error_message: str = "Недостаточно прав для этой операции.",
) -> None:
    if not has_permission(actor, permission):
        raise PermissionError(error_message)
