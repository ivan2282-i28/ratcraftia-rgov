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


def test_change_password_and_rgov_login() -> None:
    db_path = Path("data/test-auth-flows.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app

    reset_engine_cache()

    with TestClient(app) as client:
        rgov_login = client.post(
            "/api/auth/login/rgov",
            json={"login": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert rgov_login.status_code == 200
        token = rgov_login.json()["access_token"]
        assert rgov_login.json()["profile"]["login"] == "root"

        wrong_change = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "WRONG-PASSWORD",
                "new_password": "RGOV-UPDATED-ROOT",
            },
        )
        assert wrong_change.status_code == 400

        change = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "RGOV-DEFAULT_ROOT",
                "new_password": "RGOV-UPDATED-ROOT",
            },
        )
        assert change.status_code == 200
        assert change.json()["detail"] == "Пароль обновлён."

        old_login = client.post(
            "/api/auth/login/rgov",
            json={"login": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert old_login.status_code == 401

        new_rgov_login = client.post(
            "/api/auth/login/rgov",
            json={"login": "root", "password": "RGOV-UPDATED-ROOT"},
        )
        assert new_rgov_login.status_code == 200

        new_password_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "ROOT", "password": "RGOV-UPDATED-ROOT"},
        )
        assert new_password_login.status_code == 200

        universal_password_login = client.post(
            "/api/auth/login",
            json={"identifier": "root", "secret": "RGOV-UPDATED-ROOT"},
        )
        assert universal_password_login.status_code == 200

        universal_uan_login = client.post(
            "/api/auth/login",
            json={"identifier": "ROOT", "secret": "RGOV-ROOT-001"},
        )
        assert universal_uan_login.status_code == 200


def test_portal_smoke() -> None:
    db_path = Path("data/test-rgov.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import get_engine, reset_engine_cache
    from app.main import app
    from app.models import DeputyMandate, Referendum, utc_now
    from sqlmodel import Session

    reset_engine_cache()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

        admin_login = client.post(
            "/api/auth/login/password",
            json={"identifier": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]

        parliament_user = _create_user(
            client,
            admin_token,
            uin="1.26.563372",
            uan="RAT-NAV-001",
            login="navaliniy",
            permissions=[],
        )
        _create_user(
            client,
            admin_token,
            uin="3.10.900001",
            uan="RAT-IVAN-001",
            login="ivan",
            permissions=[],
        )
        deputy_users = [
            _create_user(
                client,
                admin_token,
                uin=f"7.10.90000{index}",
                uan=f"RAT-DEP-00{index}",
                login=f"deputy{index}",
                permissions=[],
            )
            for index in range(1, 10)
        ]

        with Session(get_engine()) as session:
            deputy_ids = [parliament_user["id"], *[item["id"] for item in deputy_users]]
            for seat_number, deputy_id in enumerate(deputy_ids, start=1):
                session.add(
                    DeputyMandate(
                        seat_number=seat_number,
                        deputy_id=deputy_id,
                        status="active",
                        starts_at=utc_now(),
                        ends_at=utc_now().replace(year=utc_now().year + 1),
                    )
                )
            session.commit()

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

        deputy_tokens = [parliament_token]
        for item in deputy_users:
            login = client.post(
                "/api/auth/login/password",
                json={"identifier": item["login"], "password": "ratcraftia"},
            )
            assert login.status_code == 200
            deputy_tokens.append(login.json()["access_token"])

        for token in deputy_tokens:
            vote_bill = client.post(
                f"/api/parliament/bills/{bill_id}/vote",
                headers={"Authorization": f"Bearer {token}"},
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
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={
                "title": "Поправка к конституции",
                "description": "Тест",
                "proposed_text": "Статья 2. Демонстрация одобрена.",
                "target_level": "constitution",
                "matter_type": "constitution_amendment",
                "closes_in_days": 4,
            },
        )
        assert referendum.status_code == 201
        referendum_id = referendum.json()["id"]

        for token in [parliament_token, admin_token, deputy_tokens[1]]:
            sign_ref = client.post(
                f"/api/referenda/{referendum_id}/sign",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert sign_ref.status_code == 200

        for token in [citizen_token, parliament_token, admin_token, deputy_tokens[1]]:
            vote_ref = client.post(
                f"/api/referenda/{referendum_id}/vote",
                headers={"Authorization": f"Bearer {token}"},
                json={"vote": "yes"},
            )
            assert vote_ref.status_code == 200

        with Session(get_engine()) as session:
            referendum_record = session.get(Referendum, referendum_id)
            referendum_record.closes_at = utc_now().replace(year=2020)
            session.add(referendum_record)
            session.commit()

        referenda = client.get("/api/referenda")
        assert referenda.status_code == 200

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

        org = client.post(
            "/api/admin/organizations",
            headers={"Authorization": f"Bearer {root_token}"},
            json={
                "name": "Казначейство",
                "slug": "treasury-office",
                "description": "Тестовая организация для кошелька",
            },
        )
        assert org.status_code == 201
        organization = org.json()
        assert organization["ratubles"] == 0

        directory = client.get(
            "/api/ratubles/directory",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert directory.status_code == 200
        assert any(item["kind"] == "organization" for item in directory.json())

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

        org_mint = client.post(
            "/api/ratubles/mint",
            headers={"Authorization": f"Bearer {root_token}"},
            json={
                "recipient_id": organization["id"],
                "recipient_kind": "organization",
                "amount": 900,
                "reason": "Стартовый бюджет",
            },
        )
        assert org_mint.status_code == 201
        assert org_mint.json()["recipient_kind"] == "organization"

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
                "recipient_id": organization["id"],
                "recipient_kind": "organization",
                "amount": 120,
                "reason": "Оплата пошлины",
            },
        )
        assert transfer.status_code == 201
        assert transfer.json()["kind"] == "transfer"
        assert transfer.json()["direction"] == "outgoing"
        assert transfer.json()["recipient_kind"] == "organization"

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
        assert len(ledger.json()) == 3
        assert any(item["recipient_kind"] == "organization" for item in ledger.json())

        organizations = client.get(
            "/api/admin/organizations",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert organizations.status_code == 200
        treasury_org = next(
            item for item in organizations.json() if item["slug"] == "treasury-office"
        )
        assert treasury_org["ratubles"] == 1020

        logs = client.get(
            "/api/admin/logs",
            headers={"Authorization": f"Bearer {root_token}"},
        )
        assert logs.status_code == 200
        actions = [item["action"] for item in logs.json()]
        assert "user.update" in actions
        assert "ratubles.mint" in actions
