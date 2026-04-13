from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

from .services.permissions import permissions_from_legacy_role, serialize_permissions


@dataclass(frozen=True)
class Migration:
    revision: str
    description: str
    upgrade: Callable[[Connection], None]


def _ensure_schema_migrations_table(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                revision VARCHAR(64) PRIMARY KEY,
                description VARCHAR(255) NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def _applied_revisions(connection: Connection) -> set[str]:
    rows = connection.execute(text("SELECT revision FROM schema_migrations")).all()
    return {row[0] for row in rows}


def _add_user_ratubles(connection: Connection) -> None:
    inspector = inspect(connection)
    if "user" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user")}
    if "ratubles" in columns:
        return
    connection.execute(text('ALTER TABLE "user" ADD COLUMN ratubles INTEGER NOT NULL DEFAULT 0'))


def _add_user_permissions(connection: Connection) -> None:
    inspector = inspect(connection)
    if "user" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user")}
    if "permissions" not in columns:
        connection.execute(text('ALTER TABLE "user" ADD COLUMN permissions VARCHAR NOT NULL DEFAULT ""'))
        columns.add("permissions")
    if "role" not in columns:
        return
    rows = connection.execute(
        text('SELECT id, login, role, permissions FROM "user"')
    ).mappings()
    for row in rows:
        if row["permissions"]:
            continue
        permissions = serialize_permissions(
            permissions_from_legacy_role(row["role"], login=row["login"])
        )
        connection.execute(
            text('UPDATE "user" SET permissions = :permissions WHERE id = :id'),
            {"id": row["id"], "permissions": permissions},
        )


def _create_ratubles_transaction_table(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS ratublestransaction (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                kind VARCHAR NOT NULL,
                amount INTEGER NOT NULL,
                reason VARCHAR NOT NULL DEFAULT '',
                sender_id INTEGER,
                recipient_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                FOREIGN KEY(sender_id) REFERENCES user (id),
                FOREIGN KEY(recipient_id) REFERENCES user (id),
                FOREIGN KEY(actor_id) REFERENCES user (id)
            )
            """
        )
    )


def _create_admin_log_table(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS adminlog (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                actor_id INTEGER NOT NULL,
                action VARCHAR NOT NULL,
                summary VARCHAR NOT NULL,
                reason VARCHAR NOT NULL DEFAULT '',
                target_user_id INTEGER,
                target_label VARCHAR NOT NULL DEFAULT '',
                FOREIGN KEY(actor_id) REFERENCES user (id),
                FOREIGN KEY(target_user_id) REFERENCES user (id)
            )
            """
        )
    )


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        revision="20260412_001_add_user_ratubles",
        description="Add ratubles balance to users",
        upgrade=_add_user_ratubles,
    ),
    Migration(
        revision="20260412_002_add_user_permissions",
        description="Add permissions to users and backfill legacy roles",
        upgrade=_add_user_permissions,
    ),
    Migration(
        revision="20260412_003_create_ratubles_transaction_table",
        description="Create ratubles transaction ledger table",
        upgrade=_create_ratubles_transaction_table,
    ),
    Migration(
        revision="20260412_004_create_admin_log_table",
        description="Create admin audit log table",
        upgrade=_create_admin_log_table,
    ),
)


def run_migrations(engine: Engine) -> None:
    with engine.begin() as connection:
        _ensure_schema_migrations_table(connection)
        applied_revisions = _applied_revisions(connection)
        for migration in MIGRATIONS:
            if migration.revision in applied_revisions:
                continue
            migration.upgrade(connection)
            connection.execute(
                text(
                    """
                    INSERT INTO schema_migrations (revision, description)
                    VALUES (:revision, :description)
                    """
                ),
                {
                    "revision": migration.revision,
                    "description": migration.description,
                },
            )
