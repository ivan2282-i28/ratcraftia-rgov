from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, select


def _login(client: TestClient, identifier: str, password: str) -> str:
    response = client.post(
        "/api/auth/login/password",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_user(
    client: TestClient,
    token: str,
    *,
    index: int,
    permissions: list[str] | None = None,
) -> dict:
    permissions = permissions or []
    response = client.post(
        "/api/admin/users",
        headers=_auth(token),
        json={
            "uin": f"UIN-{index:03d}",
            "uan": f"UAN-{index:03d}",
            "login": f"user{index}",
            "password": "ratcraftia",
            "first_name": f"User{index}",
            "last_name": "Citizen",
            "patronymic": "",
            "permissions": permissions,
            "position_title": "citizen",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _set_datetime(model, record_id: int, field_name: str, value) -> None:
    from app.db import get_engine

    with Session(get_engine()) as session:
        record = session.get(model, record_id)
        setattr(record, field_name, value)
        session.add(record)
        session.commit()


def test_referendum_uses_signatures_quorum_and_four_day_window() -> None:
    db_path = Path("data/test-governance-referendum.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app
    from app.models import Referendum, utc_now

    reset_engine_cache()

    with TestClient(app) as client:
        root_token = _login(client, "root", "RGOV-DEFAULT_ROOT")
        _create_user(client, root_token, index=1)
        _create_user(client, root_token, index=2)
        _create_user(client, root_token, index=3)

        user1_token = _login(client, "user1", "ratcraftia")
        user2_token = _login(client, "user2", "ratcraftia")

        create = client.post(
            "/api/referenda",
            headers=_auth(user1_token),
            json={
                "title": "Поправка о цифровом голосовании",
                "description": "Закрепить обязательное использование RGOV.",
                "proposed_text": "Статья о цифровом голосовании действует напрямую.",
                "target_level": "constitution",
                "matter_type": "constitution_amendment",
                "closes_in_days": 4,
            },
        )
        assert create.status_code == 201, create.text
        referendum = create.json()
        referendum_id = referendum["id"]
        assert referendum["status"] == "collecting_signatures"
        assert referendum["signature_count"] == 1
        assert referendum["required_signatures"] == 2
        assert referendum["required_quorum"] == 2

        sign = client.post(
            f"/api/referenda/{referendum_id}/sign",
            headers=_auth(user2_token),
        )
        assert sign.status_code == 200, sign.text
        signed = sign.json()
        assert signed["status"] == "open"
        assert signed["signature_count"] == 2

        vote1 = client.post(
            f"/api/referenda/{referendum_id}/vote",
            headers=_auth(user1_token),
            json={"vote": "yes"},
        )
        assert vote1.status_code == 200, vote1.text
        vote2 = client.post(
            f"/api/referenda/{referendum_id}/vote",
            headers=_auth(user2_token),
            json={"vote": "yes"},
        )
        assert vote2.status_code == 200, vote2.text

        _set_datetime(
            Referendum,
            referendum_id,
            "closes_at",
            utc_now().replace(year=2020),
        )

        referenda = client.get("/api/referenda")
        assert referenda.status_code == 200, referenda.text
        refreshed = next(item for item in referenda.json() if item["id"] == referendum_id)
        assert refreshed["status"] == "approved"
        assert refreshed["total_votes"] == 2
        assert refreshed["quorum_reached"] is True

        publish = client.post(
            f"/api/referenda/{referendum_id}/publish",
            headers=_auth(user1_token),
        )
        assert publish.status_code == 200, publish.text
        outcome = publish.json()
        assert outcome["referendum"]["status"] == "enacted"
        assert outcome["law"] is not None
        assert outcome["law"]["level"] == "constitution"


def test_root_overwrite_mode_can_directly_change_constitution() -> None:
    db_path = Path("data/test-governance-overwrite.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app

    reset_engine_cache()

    with TestClient(app) as client:
        root_token = _login(client, "root", "RGOV-DEFAULT_ROOT")
        auth_headers = _auth(root_token)

        laws = client.get("/api/laws")
        assert laws.status_code == 200, laws.text
        constitution = next(item for item in laws.json() if item["level"] == "constitution")

        denied = client.post(
            f"/api/admin/laws/{constitution['id']}/overwrite",
            headers=auth_headers,
            json={
                "title": constitution["title"],
                "slug": constitution["slug"],
                "level": constitution["level"],
                "current_text": "Новая редакция без overwrite mode.",
                "status": constitution["status"],
                "adopted_via": "overwrite",
                "reason": "should fail",
            },
        )
        assert denied.status_code == 403, denied.text

        updated = client.post(
            f"/api/admin/laws/{constitution['id']}/overwrite",
            headers={
                **auth_headers,
                "X-RGOV-Overwrite-Mode": "true",
            },
            json={
                "title": "Конституция Ratcraftia",
                "slug": constitution["slug"],
                "level": "constitution",
                "current_text": "Статья overwrite: root может напрямую перезаписать Конституцию в RGOV.",
                "status": "active",
                "adopted_via": "overwrite",
                "reason": "root overwrite test",
            },
        )
        assert updated.status_code == 200, updated.text
        payload = updated.json()
        assert payload["level"] == "constitution"
        assert payload["adopted_via"] == "overwrite"
        assert payload["current_text"] == "Статья overwrite: root может напрямую перезаписать Конституцию в RGOV."
        assert payload["version"] == 2


def test_parliament_election_creates_deputies_and_bills_need_quorum() -> None:
    db_path = Path("data/test-governance-parliament.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["RGOV_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.db import reset_engine_cache
    from app.main import app
    from app.models import ParliamentElection, utc_now

    reset_engine_cache()

    with TestClient(app) as client:
        root_token = _login(client, "root", "RGOV-DEFAULT_ROOT")
        created = [_create_user(client, root_token, index=index) for index in range(1, 12)]
        user_tokens = {
            item["login"]: _login(client, item["login"], "ratcraftia")
            for item in created
        }

        summary = client.get("/api/parliament/summary")
        assert summary.status_code == 200, summary.text
        election_id = summary.json()["active_election"]["id"]

        parliament_candidates = created[:10]

        for item in parliament_candidates:
            login = item["login"]
            nominate = client.post(
                f"/api/parliament/elections/{election_id}/candidates",
                headers=_auth(user_tokens[login]),
                json={"party_name": ""},
            )
            assert nominate.status_code == 200, nominate.text

        elections = client.get("/api/parliament/elections")
        assert elections.status_code == 200, elections.text
        active = elections.json()[0]
        candidates = active["candidates"]
        candidate_by_user = {candidate["user_id"]: candidate["id"] for candidate in candidates}

        def sign_candidate(candidate_user_id: int, signer_login: str) -> None:
            response = client.post(
                f"/api/parliament/elections/{election_id}/candidates/{candidate_by_user[candidate_user_id]}/sign",
                headers=_auth(user_tokens[signer_login]),
            )
            assert response.status_code == 200, response.text

        root_headers = _auth(root_token)
        first_candidate_id = parliament_candidates[0]["id"]
        second_candidate_login = parliament_candidates[1]["login"]
        for item in parliament_candidates:
            candidate_user_id = item["id"]
            response = client.post(
                f"/api/parliament/elections/{election_id}/candidates/{candidate_by_user[candidate_user_id]}/sign",
                headers=root_headers,
            )
            assert response.status_code == 200, response.text
            sign_candidate(candidate_user_id, "user11")
            extra_signer = "user1" if candidate_user_id != first_candidate_id else second_candidate_login
            sign_candidate(candidate_user_id, extra_signer)

        for voter_token in [root_token, *user_tokens.values()]:
            for item in parliament_candidates:
                candidate_user_id = item["id"]
                vote = client.post(
                    f"/api/parliament/elections/{election_id}/candidates/{candidate_by_user[candidate_user_id]}/vote",
                    headers=_auth(voter_token),
                    json={"vote": "yes"},
                )
                assert vote.status_code == 200, vote.text

        _set_datetime(
            ParliamentElection,
            election_id,
            "closes_at",
            utc_now().replace(year=2020),
        )

        refreshed_summary = client.get("/api/parliament/summary")
        assert refreshed_summary.status_code == 200, refreshed_summary.text
        summary_payload = refreshed_summary.json()
        assert len(summary_payload["deputies"]) == 10
        assert summary_payload["quorum"] == 10

        bill_create = client.post(
            "/api/parliament/bills",
            headers=_auth(user_tokens["user1"]),
            json={
                "title": "Закон о парламентском кворуме",
                "summary": "Проверка законодательного цикла.",
                "proposed_text": "Парламент работает при наличии кворума.",
                "target_level": "law",
            },
        )
        assert bill_create.status_code == 201, bill_create.text
        bill_id = bill_create.json()["id"]

        for index in range(1, 10):
            vote = client.post(
                f"/api/parliament/bills/{bill_id}/vote",
                headers=_auth(user_tokens[f"user{index}"]),
                json={"vote": "yes"},
            )
            assert vote.status_code == 200, vote.text

        bills = client.get("/api/parliament/bills")
        assert bills.status_code == 200, bills.text
        before_quorum = next(item for item in bills.json() if item["id"] == bill_id)
        assert before_quorum["status"] == "open"
        assert before_quorum["quorum_reached"] is False

        early_publish = client.post(
            f"/api/parliament/bills/{bill_id}/publish",
            headers=_auth(user_tokens["user1"]),
        )
        assert early_publish.status_code == 400

        tenth_vote = client.post(
            f"/api/parliament/bills/{bill_id}/vote",
            headers=_auth(user_tokens["user10"]),
            json={"vote": "yes"},
        )
        assert tenth_vote.status_code == 200, tenth_vote.text
        assert tenth_vote.json()["status"] == "approved"
        assert tenth_vote.json()["quorum_reached"] is True

        publish = client.post(
            f"/api/parliament/bills/{bill_id}/publish",
            headers=_auth(user_tokens["user1"]),
        )
        assert publish.status_code == 200, publish.text
        assert publish.json()["level"] == "law"
