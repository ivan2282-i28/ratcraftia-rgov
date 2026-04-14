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


def _add_org_ratubles(connection: Connection) -> None:
    inspector = inspect(connection)
    if "organization" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("organization")}
    if "ratubles" in columns:
        return
    connection.execute(
        text('ALTER TABLE organization ADD COLUMN ratubles INTEGER NOT NULL DEFAULT 0')
    )


def _upgrade_ratubles_transaction_targets(connection: Connection) -> None:
    inspector = inspect(connection)
    if "ratublestransaction" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("ratublestransaction")}
    if "recipient_org_id" in columns:
        return

    connection.execute(text("PRAGMA foreign_keys=OFF"))
    connection.execute(
        text(
            """
            CREATE TABLE ratublestransaction_new (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                kind VARCHAR NOT NULL,
                amount INTEGER NOT NULL,
                reason VARCHAR NOT NULL DEFAULT '',
                sender_id INTEGER,
                recipient_id INTEGER,
                recipient_org_id INTEGER,
                actor_id INTEGER NOT NULL,
                FOREIGN KEY(sender_id) REFERENCES user (id),
                FOREIGN KEY(recipient_id) REFERENCES user (id),
                FOREIGN KEY(recipient_org_id) REFERENCES organization (id),
                FOREIGN KEY(actor_id) REFERENCES user (id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO ratublestransaction_new (
                created_at,
                updated_at,
                id,
                kind,
                amount,
                reason,
                sender_id,
                recipient_id,
                actor_id
            )
            SELECT
                created_at,
                updated_at,
                id,
                kind,
                amount,
                reason,
                sender_id,
                recipient_id,
                actor_id
            FROM ratublestransaction
            """
        )
    )
    connection.execute(text("DROP TABLE ratublestransaction"))
    connection.execute(text("ALTER TABLE ratublestransaction_new RENAME TO ratublestransaction"))
    connection.execute(text("PRAGMA foreign_keys=ON"))


def _upgrade_referendum_constitutional_rules(connection: Connection) -> None:
    inspector = inspect(connection)
    if "referendum" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("referendum")}
    if "matter_type" not in columns:
        connection.execute(
            text(
                'ALTER TABLE referendum ADD COLUMN matter_type VARCHAR NOT NULL DEFAULT "constitution_amendment"'
            )
        )
    if "subject_user_id" not in columns:
        connection.execute(
            text("ALTER TABLE referendum ADD COLUMN subject_user_id INTEGER")
        )
    if "required_signatures" not in columns:
        connection.execute(
            text('ALTER TABLE referendum ADD COLUMN required_signatures INTEGER NOT NULL DEFAULT 1')
        )
    if "required_quorum" not in columns:
        connection.execute(
            text('ALTER TABLE referendum ADD COLUMN required_quorum INTEGER NOT NULL DEFAULT 1')
        )
    connection.execute(
        text(
            """
            UPDATE referendum
            SET
                matter_type = CASE
                    WHEN target_level = 'constitution' THEN 'constitution_amendment'
                    ELSE 'law_change'
                END,
                status = CASE
                    WHEN status IN ('approved', 'rejected', 'enacted') THEN status
                    ELSE 'collecting_signatures'
                END,
                required_signatures = CASE
                    WHEN required_signatures < 1 THEN 1
                    ELSE required_signatures
                END,
                required_quorum = CASE
                    WHEN required_quorum < 1 THEN 1
                    ELSE required_quorum
                END
            """
        )
    )


def _create_governance_tables(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parliamentelection (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                title VARCHAR NOT NULL,
                kind VARCHAR NOT NULL DEFAULT 'general',
                status VARCHAR NOT NULL DEFAULT 'open',
                seat_count INTEGER NOT NULL DEFAULT 20,
                created_by_id INTEGER,
                opens_at DATETIME NOT NULL,
                closes_at DATETIME NOT NULL,
                FOREIGN KEY(created_by_id) REFERENCES user (id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS deputymandate (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                seat_number INTEGER NOT NULL,
                deputy_id INTEGER NOT NULL,
                election_id INTEGER,
                status VARCHAR NOT NULL DEFAULT 'active',
                starts_at DATETIME NOT NULL,
                ends_at DATETIME NOT NULL,
                ended_at DATETIME,
                ended_reason VARCHAR NOT NULL DEFAULT '',
                FOREIGN KEY(deputy_id) REFERENCES user (id),
                FOREIGN KEY(election_id) REFERENCES parliamentelection (id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parliamentcandidate (
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                id INTEGER NOT NULL PRIMARY KEY,
                election_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                party_name VARCHAR NOT NULL DEFAULT '',
                status VARCHAR NOT NULL DEFAULT 'collecting_signatures',
                required_signatures INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(election_id) REFERENCES parliamentelection (id),
                FOREIGN KEY(user_id) REFERENCES user (id),
                CONSTRAINT uq_parliament_candidate_user UNIQUE (election_id, user_id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parliamentcandidatesignature (
                id INTEGER NOT NULL PRIMARY KEY,
                candidate_id INTEGER NOT NULL,
                signer_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES parliamentcandidate (id),
                FOREIGN KEY(signer_id) REFERENCES user (id),
                CONSTRAINT uq_parliament_candidate_signature UNIQUE (candidate_id, signer_id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS parliamentelectionvote (
                id INTEGER NOT NULL PRIMARY KEY,
                election_id INTEGER NOT NULL,
                voter_id INTEGER NOT NULL,
                candidate_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(election_id) REFERENCES parliamentelection (id),
                FOREIGN KEY(voter_id) REFERENCES user (id),
                FOREIGN KEY(candidate_id) REFERENCES parliamentcandidate (id),
                CONSTRAINT uq_parliament_election_vote UNIQUE (election_id, voter_id, candidate_id)
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS referendumsignature (
                id INTEGER NOT NULL PRIMARY KEY,
                referendum_id INTEGER NOT NULL,
                signer_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(referendum_id) REFERENCES referendum (id),
                FOREIGN KEY(signer_id) REFERENCES user (id),
                CONSTRAINT uq_referendum_signature UNIQUE (referendum_id, signer_id)
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
    Migration(
        revision="20260414_001_add_org_ratubles",
        description="Add ratubles balance to organizations",
        upgrade=_add_org_ratubles,
    ),
    Migration(
        revision="20260414_002_upgrade_ratubles_transaction_targets",
        description="Allow Ratubles transactions to target organizations",
        upgrade=_upgrade_ratubles_transaction_targets,
    ),
    Migration(
        revision="20260414_003_upgrade_referendum_constitutional_rules",
        description="Add signatures, quorum, and matter types to referenda",
        upgrade=_upgrade_referendum_constitutional_rules,
    ),
    Migration(
        revision="20260414_004_create_governance_tables",
        description="Create parliament elections, mandates, and signature tables",
        upgrade=_create_governance_tables,
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
