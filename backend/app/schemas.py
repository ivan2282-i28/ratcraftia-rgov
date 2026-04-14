from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    detail: str


class AuthLoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    secret: str = Field(min_length=1)


class PasswordLoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UanLoginRequest(BaseModel):
    uin: str = Field(min_length=1)
    uan: str = Field(min_length=1)


class RgovLoginRequest(BaseModel):
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile: "ProfileResponse"


class LoginChangeRequest(BaseModel):
    new_login: str = Field(min_length=3, max_length=64)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2)
    slug: str = Field(min_length=2)
    kind: str = Field(default="government")
    description: str = Field(default="")


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    kind: str
    description: str
    ratubles: int


class UserRead(BaseModel):
    id: int
    uin: str
    uan: str
    login: str
    first_name: str
    last_name: str
    patronymic: str
    full_name: str
    permissions: list[str]
    permissions_label: str
    is_active: bool
    ratubles: int
    position_title: str
    organization: OrganizationRead | None = None
    photo_url: str | None = None
    aliases: list[str] = Field(default_factory=list)
    next_login_change_at: datetime | None = None
    is_deputy: bool = False


class ProfileResponse(UserRead):
    pass


class DidTokenResponse(BaseModel):
    token: str
    expires_at: datetime
    payload: dict[str, str]


class MailCreate(BaseModel):
    to: str = Field(min_length=3)
    subject: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1)


class MailRead(BaseModel):
    id: int
    from_address: str
    to_address: str
    subject: str
    text: str
    sender_name: str
    recipient_name: str
    created_at: datetime
    read_at: datetime | None


class NewsCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    body: str = Field(min_length=3)


class NewsRead(BaseModel):
    id: int
    title: str
    body: str
    author_name: str
    created_at: datetime


class LawRead(BaseModel):
    id: int
    title: str
    slug: str
    level: str
    version: int
    status: str
    adopted_via: str
    current_text: str
    updated_at: datetime


class LawOverwriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    level: str = Field(min_length=2, max_length=32)
    current_text: str = Field(min_length=1)
    status: str = Field(default="active", min_length=2, max_length=32)
    adopted_via: str = Field(default="overwrite", min_length=2, max_length=64)
    reason: str = Field(default="", max_length=240)


class BillCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    summary: str = Field(default="")
    proposed_text: str = Field(min_length=3)
    law_id: int | None = None
    target_level: str = Field(default="law")


class VoteRequest(BaseModel):
    vote: str = Field(pattern="^(yes|no)$")


class BillRead(BaseModel):
    id: int
    title: str
    summary: str
    proposed_text: str
    law_id: int | None
    target_level: str
    status: str
    proposer_name: str
    created_at: datetime
    yes_votes: int
    no_votes: int
    total_votes: int
    quorum_required: int
    quorum_reached: bool


class DeputyRead(BaseModel):
    user_id: int
    full_name: str
    seat_number: int
    starts_at: datetime
    ends_at: datetime


class ParliamentCandidateCreate(BaseModel):
    party_name: str = Field(default="", max_length=120)


class ParliamentCandidateRead(BaseModel):
    id: int
    user_id: int
    full_name: str
    party_name: str
    status: str
    signatures: int
    required_signatures: int
    votes: int


class ParliamentElectionRead(BaseModel):
    id: int
    title: str
    kind: str
    status: str
    seat_count: int
    opens_at: datetime
    closes_at: datetime
    created_at: datetime
    total_ballots: int
    candidate_count: int
    registered_candidate_count: int
    candidates: list[ParliamentCandidateRead] = Field(default_factory=list)


class ParliamentSummaryRead(BaseModel):
    seat_count: int
    quorum: int
    vacancies: int
    deputies: list[DeputyRead] = Field(default_factory=list)
    active_election: ParliamentElectionRead | None = None


class ReferendumCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default="")
    proposed_text: str = Field(min_length=3)
    law_id: int | None = None
    target_level: str = Field(default="constitution")
    matter_type: str = Field(default="constitution_amendment")
    subject_identifier: str | None = None
    closes_in_days: int = Field(default=4, ge=4, le=4)


class ReferendumRead(BaseModel):
    id: int
    title: str
    description: str
    proposed_text: str
    law_id: int | None
    target_level: str
    matter_type: str
    status: str
    proposer_name: str
    subject_user_id: int | None
    subject_name: str | None
    opens_at: datetime
    closes_at: datetime
    created_at: datetime
    signature_count: int
    required_signatures: int
    yes_votes: int
    no_votes: int
    total_votes: int
    required_quorum: int
    quorum_reached: bool


class ReferendumOutcomeRead(BaseModel):
    referendum: ReferendumRead
    law: LawRead | None = None
    detail: str


class PermissionChangeRequest(BaseModel):
    permissions: list[str] = Field(default_factory=list)


class HireRequest(BaseModel):
    org_slug: str = Field(min_length=2)
    position_title: str = Field(min_length=2)


class UserCreate(BaseModel):
    uin: str = Field(min_length=3)
    uan: str = Field(min_length=3)
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    patronymic: str = Field(default="")
    permissions: list[str] = Field(default_factory=list)
    org_slug: str | None = None
    position_title: str = Field(default="")
    photo_url: str | None = None


class UserUpdate(BaseModel):
    uin: str = Field(min_length=3)
    uan: str = Field(min_length=3)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    patronymic: str = Field(default="")


class UserDirectoryRead(BaseModel):
    id: int
    uin: str
    login: str
    full_name: str


class RatublesDirectoryEntryRead(BaseModel):
    id: int
    kind: str
    code: str
    full_name: str
    subtitle: str = ""


class RatublesTransferRequest(BaseModel):
    recipient_id: int = Field(gt=0)
    recipient_kind: str = Field(default="user", pattern="^(user|organization)$")
    amount: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=240)


class RatublesMintRequest(BaseModel):
    recipient_id: int = Field(gt=0)
    recipient_kind: str = Field(default="user", pattern="^(user|organization)$")
    amount: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=240)


class RatublesTransactionRead(BaseModel):
    id: int
    kind: str
    direction: str
    amount: int
    reason: str
    sender_kind: str | None = None
    sender_name: str | None
    sender_code: str | None = None
    sender_uin: str | None
    recipient_kind: str
    recipient_name: str | None
    recipient_code: str | None = None
    recipient_uin: str | None
    actor_name: str | None
    created_at: datetime


class AdminLogRead(BaseModel):
    id: int
    action: str
    summary: str
    reason: str
    actor_name: str
    target_name: str | None
    created_at: datetime


class DeveloperAppCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=64)
    description: str = Field(default="", max_length=500)
    website_url: str = Field(default="", max_length=255)
    redirect_uris: list[str] = Field(min_length=1)
    allowed_scopes: list[str] = Field(default_factory=lambda: ["profile.basic"])


class DeveloperAppRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    website_url: str
    redirect_uris: list[str]
    allowed_scopes: list[str]
    client_id: str
    status: str
    review_note: str
    owner_name: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    last_secret_rotated_at: datetime | None = None


class DeveloperAppCreateResponse(DeveloperAppRead):
    client_secret: str


class DeveloperAppSecretResponse(BaseModel):
    client_id: str
    client_secret: str
    rotated_at: datetime


class DeveloperAppReviewRequest(BaseModel):
    status: str = Field(pattern="^(approved|rejected|revoked)$")
    review_note: str = Field(default="", max_length=500)


class OAuthAuthorizationRequest(BaseModel):
    client_id: str = Field(min_length=8, max_length=128)
    redirect_uri: str = Field(min_length=1, max_length=500)
    response_type: str = Field(default="code", pattern="^code$")
    scope: str = Field(default="profile.basic", max_length=255)
    state: str | None = Field(default=None, max_length=255)


class OAuthAuthorizationResponse(BaseModel):
    redirect_to: str
    expires_at: datetime | None = None


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str


class OAuthUserInfoResponse(BaseModel):
    sub: str
    client_id: str
    scopes: list[str]
    uin: str
    login: str
    first_name: str
    last_name: str
    patronymic: str
    full_name: str
    organization_slug: str | None = None
    organization_name: str | None = None
    position_title: str | None = None
    permissions: list[str] | None = None


class PublicOAuthAppRead(BaseModel):
    client_id: str
    name: str
    description: str
    website_url: str
    status: str
    owner_name: str
    allowed_scopes: list[str]


class PushConfigResponse(BaseModel):
    public_vapid_key: str
    contact_email: str


class PushSubscriptionCreate(BaseModel):
    subscription: dict[str, Any]
    user_agent: str = Field(default="")


class PushSubscriptionRemove(BaseModel):
    endpoint: str = Field(min_length=1)


TokenResponse.model_rebuild()
