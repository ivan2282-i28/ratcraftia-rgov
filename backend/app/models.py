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
    ratubles: int = Field(default=0, nullable=False)


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
    recipient_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    recipient_org_id: int | None = Field(
        default=None,
        foreign_key="organization.id",
        index=True,
    )
    actor_id: int = Field(foreign_key="user.id", index=True)


class AdminLog(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="user.id", index=True)
    action: str = Field(index=True)
    summary: str
    reason: str = Field(default="", nullable=False)
    target_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    target_label: str = Field(default="", nullable=False)


class OAuthApplication(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    slug: str = Field(index=True, unique=True)
    description: str = Field(default="")
    website_url: str = Field(default="")
    redirect_uris_json: str = Field(default="[]", nullable=False)
    allowed_scopes: str = Field(default="profile.basic", nullable=False)
    client_id: str = Field(index=True, unique=True)
    client_secret_hash: str
    status: str = Field(default="pending", index=True)
    review_note: str = Field(default="", nullable=False)
    approved_by_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    approved_at: datetime | None = Field(default=None)
    last_secret_rotated_at: datetime | None = Field(default=None)


class OAuthAuthorizationCode(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="oauthapplication.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    code: str = Field(index=True, unique=True)
    redirect_uri: str
    scopes: str = Field(default="profile.basic", nullable=False)
    expires_at: datetime = Field(nullable=False)
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class OAuthAccessToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="oauthapplication.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token_id: str = Field(index=True, unique=True)
    scopes: str = Field(default="profile.basic", nullable=False)
    expires_at: datetime = Field(nullable=False)
    revoked_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


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


class DeputyMandate(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seat_number: int = Field(index=True)
    deputy_id: int = Field(foreign_key="user.id", index=True)
    election_id: int | None = Field(default=None, foreign_key="parliamentelection.id")
    status: str = Field(default="active", index=True)
    starts_at: datetime = Field(default_factory=utc_now)
    ends_at: datetime = Field(default_factory=utc_now)
    ended_at: datetime | None = Field(default=None)
    ended_reason: str = Field(default="")


class ParliamentElection(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    kind: str = Field(default="general", index=True)
    status: str = Field(default="open", index=True)
    seat_count: int = Field(default=20)
    created_by_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    opens_at: datetime = Field(default_factory=utc_now)
    closes_at: datetime = Field(default_factory=lambda: utc_now() + timedelta(days=4))


class ParliamentCandidate(Timestamped, table=True):
    __table_args__ = (
        UniqueConstraint("election_id", "user_id", name="uq_parliament_candidate_user"),
    )

    id: int | None = Field(default=None, primary_key=True)
    election_id: int = Field(foreign_key="parliamentelection.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    party_name: str = Field(default="")
    status: str = Field(default="collecting_signatures", index=True)
    required_signatures: int = Field(default=1)


class ParliamentCandidateSignature(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "signer_id",
            name="uq_parliament_candidate_signature",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="parliamentcandidate.id", index=True)
    signer_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class ParliamentElectionVote(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "election_id",
            "voter_id",
            "candidate_id",
            name="uq_parliament_election_vote",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    election_id: int = Field(foreign_key="parliamentelection.id", index=True)
    voter_id: int = Field(foreign_key="user.id", index=True)
    candidate_id: int = Field(foreign_key="parliamentcandidate.id", index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Referendum(Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str = Field(default="")
    proposed_text: str
    law_id: int | None = Field(default=None, foreign_key="law.id")
    target_level: str = Field(default="constitution", index=True)
    matter_type: str = Field(default="constitution_amendment", index=True)
    status: str = Field(default="collecting_signatures", index=True)
    proposer_id: int = Field(foreign_key="user.id")
    subject_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    required_signatures: int = Field(default=1)
    required_quorum: int = Field(default=1)
    opens_at: datetime = Field(default_factory=utc_now)
    closes_at: datetime = Field(default_factory=utc_now)


class ReferendumVote(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("referendum_id", "voter_id", name="uq_referendum_voter"),
    )

    id: int | None = Field(default=None, primary_key=True)
    referendum_id: int = Field(foreign_key="referendum.id", index=True)
    voter_id: int = Field(foreign_key="user.id", index=True)
    vote: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class ReferendumSignature(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("referendum_id", "signer_id", name="uq_referendum_signature"),
    )

    id: int | None = Field(default=None, primary_key=True)
    referendum_id: int = Field(foreign_key="referendum.id", index=True)
    signer_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
