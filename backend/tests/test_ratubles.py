from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlmodel import Session, select

from app.db import get_engine, init_db, reset_engine_cache
from app.migrations import MIGRATIONS
from app.models import User
from app.schemas import UserCreate
from app.services.permissions import serialize_permissions
from app.services.portal import create_user


def _configure_database(monkeypatch, db_path: Path) -> None:
    monkeypatch.setenv("RGOV_DATABASE_URL", f"sqlite:///{db_path}")
    reset_engine_cache()


def test_create_user_defaults_ratubles_to_zero(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "ratubles-default.db"
    _configure_database(monkeypatch, db_path)
    init_db()

    with Session(get_engine()) as session:
        created = create_user(
            session,
            UserCreate(
                uin="100001",
                uan="200001",
                login="tester",
                password="secret123",
                first_name="Test",
                last_name="User",
            ),
        )
        stored_user = session.exec(select(User).where(User.login == "tester")).one()

    assert created.ratubles == 0
    assert stored_user.ratubles == 0


def test_init_db_records_schema_migrations_once(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "schema-migrations.db"
    _configure_database(monkeypatch, db_path)

    init_db()
    init_db()

    connection = sqlite3.connect(db_path)
    revisions = connection.execute(
        "SELECT revision FROM schema_migrations ORDER BY revision"
    ).fetchall()
    connection.close()

    assert revisions == [(migration.revision,) for migration in MIGRATIONS]


def test_init_db_adds_ratubles_to_existing_user_table(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "ratubles-migration.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE user (
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            id INTEGER NOT NULL PRIMARY KEY,
            uin VARCHAR NOT NULL,
            uan VARCHAR NOT NULL,
            login VARCHAR NOT NULL,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL,
            patronymic VARCHAR NOT NULL,
            password_hash VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            is_active BOOLEAN NOT NULL,
            org_id INTEGER,
            position_title VARCHAR NOT NULL,
            photo_url VARCHAR,
            login_changed_at DATETIME
        )
        """
    )
    connection.execute(
        """
        INSERT INTO user (
            created_at,
            updated_at,
            id,
            uin,
            uan,
            login,
            first_name,
            last_name,
            patronymic,
            password_hash,
            role,
            is_active,
            org_id,
            position_title,
            photo_url,
            login_changed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "2026-01-01T00:00:00+00:00",
            "2026-01-01T00:00:00+00:00",
            1,
            "OLD001",
            "OLDUAN001",
            "legacy-user",
            "Legacy",
            "User",
            "",
            "hash",
            "parliament_member",
            1,
            None,
            "",
            None,
            None,
        ),
    )
    connection.commit()
    connection.close()

    _configure_database(monkeypatch, db_path)
    init_db()

    connection = sqlite3.connect(db_path)
    columns = {row[1] for row in connection.execute('PRAGMA table_info("user")')}
    ratubles = connection.execute('SELECT ratubles FROM "user" WHERE id = 1').fetchone()
    permissions = connection.execute('SELECT permissions FROM "user" WHERE id = 1').fetchone()
    revisions = connection.execute(
        "SELECT revision FROM schema_migrations ORDER BY revision"
    ).fetchall()
    connection.close()

    assert "ratubles" in columns
    assert "permissions" in columns
    assert ratubles == (0,)
    assert permissions == (serialize_permissions(["bills.manage", "referenda.manage"]),)
    assert revisions == [(migration.revision,) for migration in MIGRATIONS]
