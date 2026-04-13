from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    detail: str


class PasswordLoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UanLoginRequest(BaseModel):
    uin: str = Field(min_length=1)
    uan: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile: "ProfileResponse"


class LoginChangeRequest(BaseModel):
    new_login: str = Field(min_length=3, max_length=64)


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


class ReferendumCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default="")
    proposed_text: str = Field(min_length=3)
    law_id: int | None = None
    target_level: str = Field(default="constitution")
    closes_in_days: int = Field(default=7, ge=1, le=30)


class ReferendumRead(BaseModel):
    id: int
    title: str
    description: str
    proposed_text: str
    law_id: int | None
    target_level: str
    status: str
    proposer_name: str
    opens_at: datetime
    closes_at: datetime
    created_at: datetime
    yes_votes: int
    no_votes: int


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


class RatublesTransferRequest(BaseModel):
    recipient_id: int = Field(gt=0)
    amount: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=240)


class RatublesMintRequest(BaseModel):
    recipient_id: int = Field(gt=0)
    amount: int = Field(gt=0)
    reason: str = Field(min_length=1, max_length=240)


class RatublesTransactionRead(BaseModel):
    id: int
    kind: str
    direction: str
    amount: int
    reason: str
    sender_name: str | None
    sender_uin: str | None
    recipient_name: str | None
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


class PushConfigResponse(BaseModel):
    public_vapid_key: str
    contact_email: str


class PushSubscriptionCreate(BaseModel):
    subscription: dict[str, Any]
    user_agent: str = Field(default="")


class PushSubscriptionRemove(BaseModel):
    endpoint: str = Field(min_length=1)


TokenResponse.model_rebuild()
