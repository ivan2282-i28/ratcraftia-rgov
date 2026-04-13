from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db import get_engine, reset_engine_cache
from app.models import PushSubscription


def _configure_database(monkeypatch, db_path: Path) -> None:
    monkeypatch.setenv("RGOV_DATABASE_URL", f"sqlite:///{db_path}")
    reset_engine_cache()


def test_register_and_unregister_push_subscription(
    monkeypatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "notifications.db"
    _configure_database(monkeypatch, db_path)

    from app.main import app

    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login/password",
            json={"identifier": "root", "password": "RGOV-DEFAULT_ROOT"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        config = client.get("/api/notifications/config", headers=headers)
        assert config.status_code == 200
        assert config.json()["public_vapid_key"]

        payload = {
            "subscription": {
                "endpoint": "https://push.example.test/subscription-1",
                "keys": {"auth": "auth-key", "p256dh": "public-key"},
            },
            "user_agent": "pytest",
        }

        subscribe = client.post(
            "/api/notifications/subscriptions",
            headers=headers,
            json=payload,
        )
        assert subscribe.status_code == 200

        payload["subscription"]["keys"]["auth"] = "auth-key-updated"
        resubscribe = client.post(
            "/api/notifications/subscriptions",
            headers=headers,
            json=payload,
        )
        assert resubscribe.status_code == 200

        with Session(get_engine()) as session:
            records = session.exec(select(PushSubscription)).all()

        assert len(records) == 1
        assert records[0].endpoint == "https://push.example.test/subscription-1"
        assert records[0].user_agent == "pytest"
        assert (
            json.loads(records[0].subscription_json)["keys"]["auth"]
            == "auth-key-updated"
        )

        unsubscribe = client.post(
            "/api/notifications/subscriptions/unregister",
            headers=headers,
            json={"endpoint": "https://push.example.test/subscription-1"},
        )
        assert unsubscribe.status_code == 200

        with Session(get_engine()) as session:
            records = session.exec(select(PushSubscription)).all()

        assert records == []
