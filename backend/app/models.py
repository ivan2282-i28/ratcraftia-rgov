from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)


class Organization(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(index=True, unique=True)
    kind: str = Field(default="government")
    description: str = Field(default="")


class User(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uin: str = Field(index=True, unique=True)
    uan: str = Field(index=True, unique=True)
    login: str = Field(index=True, unique=True)
    first_name: str
    last_name: str
    patronymic: str = Field(default="")
    password_hash: str
    permissions: str = Field(default="", nullable=False)
    is_active: bool = Field(default=True)
    ratubles: int = Field(default=0, nullable=False)
    org_id: int | None = Field(default=None, foreign_key="organization.id")
    position_title: str = Field(default="")
    photo_url: str | None = Field(default=None)
    login_changed_at: datetime | None = Field(default=None)


class RatublesTransaction(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    kind: str = Field(index=True)
    amount: int = Field(nullable=False)
    reason: str = Field(default="", nullable=False)
    sender_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    recipient_id: int = Field(foreign_key="user.id", index=True)
    actor_id: int = Field(foreign_key="user.id", index=True)


class AdminLog(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="user.id", index=True)
    action: str = Field(index=True)
    summary: str
    reason: str = Field(default="", nullable=False)
    target_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    target_label: str = Field(default="", nullable=False)


class PushSubscription(Timestamped, table=True):
    __tablename__ = "push_subscription"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    endpoint: str = Field(index=True, unique=True)
    subscription_json: str
    user_agent: str = Field(default="")
    last_success_at: datetime | None = Field(default=None)


class MailMessage(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id", index=True)
    recipient_id: int = Field(foreign_key="user.id", index=True)
    from_address: str
    to_address: str
    subject: str
    text: str
    read_at: datetime | None = Field(default=None)


class NewsPost(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    body: str
    author_id: int = Field(foreign_key="user.id")


class Law(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(index=True, unique=True)
    level: str = Field(default="law", index=True)
    current_text: str
    version: int = Field(default=1)
    status: str = Field(default="active", index=True)
    adopted_via: str = Field(default="bootstrap")
    author_id: int | None = Field(default=None, foreign_key="user.id")
    source_bill_id: int | None = Field(default=None, foreign_key="bill.id")
    source_referendum_id: int | None = Field(default=None, foreign_key="referendum.id")


class Bill(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    summary: str = Field(default="")
    proposed_text: str
    law_id: int | None = Field(default=None, foreign_key="law.id")
    target_level: str = Field(default="law", index=True)
    status: str = Field(default="open", index=True)
    proposer_id: int = Field(foreign_key="user.id")


class BillVote(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("bill_id", "voter_id", name="uq_bill_voter"),)

    id: int | None = Field(default=None, primary_key=True)
    bill_id: int = Field(foreign_key="bill.id", index=True)
    voter_id: int = Field(foreign_key="user.id", index=True)
    vote: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Referendum(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = Field(default="")
    proposed_text: str
    law_id: int | None = Field(default=None, foreign_key="law.id")
    target_level: str = Field(default="constitution", index=True)
    status: str = Field(default="open", index=True)
    proposer_id: int = Field(foreign_key="user.id")
    opens_at: datetime = Field(default_factory=utc_now)
    closes_at: datetime = Field(default_factory=lambda: utc_now() + timedelta(days=7))


class ReferendumVote(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("referendum_id", "voter_id", name="uq_referendum_voter"),
    )

    id: int | None = Field(default=None, primary_key=True)
    referendum_id: int = Field(foreign_key="referendum.id", index=True)
    voter_id: int = Field(foreign_key="user.id", index=True)
    vote: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
