from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient


def _create_user(
    client: TestClient,
    token: str,
    *,
    uin: str,
    uan: str,
    login: str,
    permissions: list[str],
) -> dict:
    response = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "uin": uin,
            "uan": uan,
            "login": login,
            "password": "ratcraftia",
            "first_name": login.title(),
            "last_name": "Test",
            "patronymic": "",
            "permissions": permissions,
            "position_title": ", ".join(permissions) or "citizen",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_bootstrap_creates_only_root_account() -> None:
    db_path = Path("data/test-root-only.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app

    reset_engine_cache()

    with TestClient(app) as client:
        root_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert root_login.status_code == 200
        root_token = root_login.json()["access_token"]

        admin_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "admin", "password": "ratcraftia"},
        )
        assert admin_login.status_code == 401

        users = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert users.status_code == 200
        payload = users.json()
        assert len(payload) == 1
        assert payload[0]["login"] == "root"
        assert payload[0]["permissions"] == ["*"]


def test_portal_smoke() -> None:
    db_path = Path("data/test-rgov.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app

    reset_engine_cache()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

        admin_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]

        _create_user(
            client,
            admin_token,
            uin="1.26.563372",
            uan="RAT-NAV-001",
            login="navaliniy",
            permissions=["bills.manage", "referenda.manage"],
        )
        _create_user(
            client,
            admin_token,
            uin="3.10.900001",
            uan="RAT-IVAN-001",
            login="ivan",
            permissions=[],
        )

        parliament_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "navaliniy", "password": "ratcraftia"},
        )
        assert parliament_login.status_code == 200
        parliament_token = parliament_login.json()["access_token"]

        citizen_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "ivan", "password": "ratcraftia"},
        )
        assert citizen_login.status_code == 200
        citizen_token = citizen_login.json()["access_token"]

        did = client.get(
            "/api/did/me/token",
            headers={"Authorization": f"Bearer {citizen_token}"},
        )
        assert did.status_code == 200
        assert did.json()["payload"]["DID"] == "true"

        mail = client.post(
            "/api/mail/messages",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"to": "navaliniy@fn", "subject": "Проверка", "text": "Тест GovMail"},
        )
        assert mail.status_code == 201

        bill = client.post(
            "/api/parliament/bills",
            headers={"Authorization": f"Bearer {parliament_token}"},
            json={
                "title": "Закон о цифровом архиве",
                "summary": "Тестовый закон",
                "proposed_text": "Архив создаётся.",
                "target_level": "law",
            },
        )
        assert bill.status_code == 201
        bill_id = bill.json()["id"]

        vote_bill = client.post(
            f"/api/parliament/bills/{bill_id}/vote",
            headers={"Authorization": f"Bearer {parliament_token}"},
            json={"vote": "yes"},
        )
        assert vote_bill.status_code == 200

        publish_bill = client.post(
            f"/api/parliament/bills/{bill_id}/publish",
            headers={"Authorization": f"Bearer {parliament_token}"},
        )
        assert publish_bill.status_code == 200

        referendum = client.post(
            "/api/referenda",
            headers={"Authorization": f"Bearer {parliament_token}"},
            json={
                "title": "Поправка к конституции",
                "description": "Тест",
                "proposed_text": "Статья 2. Демонстрация одобрена.",
                "target_level": "constitution",
            },
        )
        assert referendum.status_code == 201
        referendum_id = referendum.json()["id"]

        vote_ref = client.post(
            f"/api/referenda/{referendum_id}/vote",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={"vote": "yes"},
        )
        assert vote_ref.status_code == 200

        publish_ref = client.post(
            f"/api/referenda/{referendum_id}/publish",
            headers={"Authorization": f"Bearer {parliament_token}"},
        )
        assert publish_ref.status_code == 200

        laws = client.get("/api/laws")
        assert laws.status_code == 200
        assert len(laws.json()) >= 2


def test_admin_logs_and_ratubles_history() -> None:
    db_path = Path("data/test-admin-ratubles.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app

    reset_engine_cache()

    with TestClient(app) as client:
        root_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert root_login.status_code == 200
        root_token = root_login.json()["access_token"]

        treasury = _create_user(
            client,
            root_token,
            uin="8.10.100001",
            uan="RAT-TREASURY-001",
            login="treasury",
            permissions=[],
        )
        citizen = _create_user(
            client,
            root_token,
            uin="8.10.100002",
            uan="RAT-CITIZEN-001",
            login="citizen",
            permissions=[],
        )

        users = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert users.status_code == 200
        citizen_record = next(
            item for item in users.json() if item["id"] == citizen["id"]
        )
        assert citizen_record["uan"] == "RAT-CITIZEN-001"

        update = client.patch(
            f"/api/admin/users/{citizen['id']}",
            headers={"Authorization": f"Bearer {root_token}"},
            json={
                "uin": "8.10.100099",
                "uan": "RAT-CITIZEN-099",
                "first_name": "Edited",
                "last_name": "Citizen",
                "patronymic": "Tester",
            },
        )
        assert update.status_code == 200
        assert update.json()["uin"] == "8.10.100099"
        assert update.json()["uan"] == "RAT-CITIZEN-099"

        mint = client.post(
            "/api/ratubles/mint",
            headers={"Authorization": f"Bearer {root_token}"},
            json={
                "recipient_id": citizen["id"],
                "amount": 300,
                "reason": "Стартовый грант",
            },
        )
        assert mint.status_code == 201
        assert mint.json()["kind"] == "mint"

        citizen_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "citizen", "password": "ratcraftia"},
        )
        assert citizen_login.status_code == 200
        citizen_token = citizen_login.json()["access_token"]

        transfer = client.post(
            "/api/ratubles/transfer",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={
                "recipient_id": treasury["id"],
                "amount": 120,
                "reason": "Оплата пошлины",
            },
        )
        assert transfer.status_code == 201
        assert transfer.json()["kind"] == "transfer"
        assert transfer.json()["direction"] == "outgoing"

        history = client.get(
            "/api/ratubles/transactions",
            headers={"Authorization": f"Bearer {citizen_token}"},
        )
        assert history.status_code == 200
        assert [item["kind"] for item in history.json()] == ["transfer", "mint"]

        ledger = client.get(
            "/api/ratubles/ledger",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert ledger.status_code == 200
        assert len(ledger.json()) == 2

        logs = client.get(
            "/api/admin/logs",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert logs.status_code == 200
        actions = [item["action"] for item in logs.json()]
        assert "user.update" in actions
        assert "ratubles.mint" in actions
