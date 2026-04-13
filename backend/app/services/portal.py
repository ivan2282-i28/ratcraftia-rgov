from __future__ import annotations

from calendar import monthrange
from datetime import timedelta, timezone
from math import ceil
import re
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from ..core.config import get_settings
from ..core.security import get_password_hash, verify_password
from ..models import (
    AdminLog,
    Bill,
    BillVote,
    DeputyMandate,
    Law,
    MailMessage,
    NewsPost,
    Organization,
    ParliamentCandidate,
    ParliamentCandidateSignature,
    ParliamentElection,
    ParliamentElectionVote,
    RatublesTransaction,
    Referendum,
    ReferendumSignature,
    ReferendumVote,
    User,
    utc_now,
)
from ..schemas import (
    AdminLogRead,
    BillCreate,
    BillRead,
    DeputyRead,
    HireRequest,
    LawRead,
    MailCreate,
    MailRead,
    NewsCreate,
    NewsRead,
    OrganizationCreate,
    OrganizationRead,
    ParliamentCandidateCreate,
    ParliamentCandidateRead,
    ParliamentElectionRead,
    ParliamentSummaryRead,
    ProfileResponse,
    PasswordChangeRequest,
    RatublesDirectoryEntryRead,
    RatublesMintRequest,
    RatublesTransactionRead,
    RatublesTransferRequest,
    ReferendumCreate,
    ReferendumOutcomeRead,
    ReferendumRead,
    UserCreate,
    UserRead,
    UserUpdate,
)
from .notifications import notify_all_users, notify_users
from .permissions import (
    ADMIN_LOGS_READ_PERMISSION,
    NEWS_MANAGE_PERMISSION,
    ORGS_CREATE_PERMISSION,
    PERSONNEL_MANAGE_PERMISSION,
    PRESET_PERMISSIONS,
    RATUBLES_MINT_PERMISSION,
    USERS_UPDATE_PERMISSION,
    USER_PERMISSIONS_WRITE_PERMISSION,
    WILDCARD_PERMISSION,
    normalize_permissions,
    permissions_label,
    require_permission,
    serialize_permissions,
)

LETTER_MAP = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "E",
    "Ё": "E",
    "Ж": "Zh",
    "З": "Z",
    "И": "I",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "Kh",
    "Ц": "Ts",
    "Ч": "Ch",
    "Ш": "Sh",
    "Щ": "Sch",
    "Ы": "Y",
    "Э": "E",
    "Ю": "Yu",
    "Я": "Ya",
}

PARLIAMENT_SEAT_COUNT = 20
PARLIAMENT_QUORUM = PARLIAMENT_SEAT_COUNT // 2
PARLIAMENT_ELECTION_DURATION_DAYS = 4
REFERENDUM_DURATION_DAYS = 4
DEPUTY_TERM_MONTHS = 6


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _local_date(value):
    zone = ZoneInfo(get_settings().local_timezone)
    return _as_utc(value).astimezone(zone).date()


def touch(model) -> None:
    model.updated_at = utc_now()


def full_name(user: User) -> str:
    parts = [user.last_name, user.first_name, user.patronymic]
    return " ".join(part for part in parts if part).strip()


def _latin_initial(value: str) -> str:
    if not value:
        return ""
    first = value[0].upper()
    return LETTER_MAP.get(first, first)


def initials_code(user: User) -> str:
    return "".join(
        [
            _latin_initial(user.last_name),
            _latin_initial(user.first_name),
            _latin_initial(user.patronymic),
        ]
    )


def get_org(session: Session, user: User) -> Organization | None:
    if user.org_id is None:
        return None
    return session.get(Organization, user.org_id)


def aliases_for_user(session: Session, user: User) -> list[str]:
    aliases = [f"{user.login}@fn", f"{user.uin}@citizen"]
    org = get_org(session, user)
    if org:
        aliases.append(f"{initials_code(user)}.{org.slug}@gov")
    return aliases


def serialize_org(org: Organization) -> OrganizationRead:
    return OrganizationRead.model_validate(org)


def _mask_uan(uan: str) -> str:
    if len(uan) <= 4:
        return "*" * len(uan)
    return f"{'*' * (len(uan) - 4)}{uan[-4:]}"


def serialize_user(session: Session, user: User, *, show_uan: bool = False) -> UserRead:
    org = get_org(session, user)
    next_login_change_at = None
    if user.login_changed_at:
        next_login_change_at = user.login_changed_at + timedelta(days=1)
    return UserRead(
        id=user.id,
        uin=user.uin,
        uan=user.uan if show_uan else _mask_uan(user.uan),
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        full_name=full_name(user),
        permissions=normalize_permissions(user.permissions),
        permissions_label=permissions_label(user.permissions),
        is_active=user.is_active,
        ratubles=user.ratubles,
        position_title=user.position_title,
        organization=serialize_org(org) if org else None,
        photo_url=user.photo_url,
        aliases=aliases_for_user(session, user),
        next_login_change_at=next_login_change_at,
        is_deputy=_is_active_deputy(session, user.id),
    )


def serialize_profile(session: Session, user: User) -> ProfileResponse:
    return ProfileResponse(**serialize_user(session, user, show_uan=True).model_dump())


def serialize_user_directory(user: User) -> RatublesDirectoryEntryRead:
    return RatublesDirectoryEntryRead(
        id=user.id,
        kind="user",
        code=user.uin,
        full_name=full_name(user),
        subtitle=f"@{user.login}",
    )


def serialize_org_directory(org: Organization) -> RatublesDirectoryEntryRead:
    return RatublesDirectoryEntryRead(
        id=org.id,
        kind="organization",
        code=org.slug,
        full_name=org.name,
        subtitle="Государственная организация",
    )


def _record_admin_log(
    session: Session,
    actor: User,
    *,
    action: str,
    summary: str,
    target_user: User | None = None,
    target_label: str = "",
    reason: str = "",
) -> None:
    session.add(
        AdminLog(
            actor_id=actor.id,
            action=action,
            summary=summary.strip(),
            reason=reason.strip(),
            target_user_id=target_user.id if target_user else None,
            target_label=(target_label or (full_name(target_user) if target_user else "")).strip(),
        )
    )


def serialize_admin_log(session: Session, entry: AdminLog) -> AdminLogRead:
    actor = session.get(User, entry.actor_id)
    target_user = session.get(User, entry.target_user_id) if entry.target_user_id else None
    return AdminLogRead(
        id=entry.id,
        action=entry.action,
        summary=entry.summary,
        reason=entry.reason,
        actor_name=full_name(actor) if actor else "Неизвестно",
        target_name=full_name(target_user) if target_user else (entry.target_label or None),
        created_at=entry.created_at,
    )


def serialize_ratubles_transaction(
    session: Session,
    transaction: RatublesTransaction,
    *,
    viewer_id: int | None = None,
) -> RatublesTransactionRead:
    sender = session.get(User, transaction.sender_id) if transaction.sender_id else None
    recipient = session.get(User, transaction.recipient_id) if transaction.recipient_id else None
    recipient_org = (
        session.get(Organization, transaction.recipient_org_id)
        if transaction.recipient_org_id
        else None
    )
    actor = session.get(User, transaction.actor_id)
    direction = "neutral"
    if viewer_id is not None:
        if transaction.sender_id == viewer_id:
            direction = "outgoing"
        elif transaction.recipient_id == viewer_id:
            direction = "incoming"
    return RatublesTransactionRead(
        id=transaction.id,
        kind=transaction.kind,
        direction=direction,
        amount=transaction.amount,
        reason=transaction.reason,
        sender_kind="user" if sender else None,
        sender_name=full_name(sender) if sender else None,
        sender_code=sender.uin if sender else None,
        sender_uin=sender.uin if sender else None,
        recipient_kind="organization" if recipient_org else "user",
        recipient_name=recipient_org.name if recipient_org else (full_name(recipient) if recipient else None),
        recipient_code=recipient_org.slug if recipient_org else (recipient.uin if recipient else None),
        recipient_uin=recipient.uin if recipient else None,
        actor_name=full_name(actor) if actor else None,
        created_at=transaction.created_at,
    )


def _resolve_ratubles_recipient(
    session: Session,
    recipient_id: int,
    recipient_kind: str,
) -> tuple[User | None, Organization | None]:
    normalized_kind = recipient_kind.strip().lower()
    if normalized_kind == "organization":
        organization = session.get(Organization, recipient_id)
        if not organization:
            raise ValueError("Организация не найдена.")
        return None, organization

    recipient = session.get(User, recipient_id)
    if not recipient or not recipient.is_active:
        raise ValueError("Получатель не найден.")
    return recipient, None


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w]+", "-", value.lower(), flags=re.UNICODE).strip("-")
    return slug or f"law-{int(utc_now().timestamp())}"


def ensure_unique_slug(session: Session, base_slug: str) -> str:
    slug = base_slug
    index = 2
    while session.exec(select(Law).where(Law.slug == slug)).first():
        slug = f"{base_slug}-{index}"
        index += 1
    return slug


def _add_calendar_months(value, months: int):
    normalized = _as_utc(value)
    month_index = normalized.month - 1 + months
    year = normalized.year + month_index // 12
    month = month_index % 12 + 1
    day = min(normalized.day, monthrange(year, month)[1])
    return normalized.replace(year=year, month=month, day=day)


def _active_citizens(session: Session) -> list[User]:
    return session.exec(
        select(User)
        .where(User.is_active == True)  # noqa: E712
        .order_by(User.last_name, User.first_name, User.id)
    ).all()


def _population_count(session: Session) -> int:
    return len(_active_citizens(session))


def _signature_requirement(session: Session) -> int:
    population = _population_count(session)
    if population >= 10_000:
        return 10_000
    return max(1, ceil(population / 3))


def _referendum_quorum_requirement(session: Session) -> int:
    return max(1, ceil(_population_count(session) / 3))


def _is_active_deputy(session: Session, user_id: int | None) -> bool:
    if user_id is None:
        return False
    _refresh_expired_mandates(session)
    mandate = session.exec(
        select(DeputyMandate).where(
            DeputyMandate.deputy_id == user_id,
            DeputyMandate.status == "active",
        )
    ).first()
    return mandate is not None


def _active_deputy_mandates(session: Session) -> list[DeputyMandate]:
    _refresh_expired_mandates(session)
    return session.exec(
        select(DeputyMandate)
        .where(DeputyMandate.status == "active")
        .order_by(DeputyMandate.seat_number, DeputyMandate.starts_at)
    ).all()


def _has_wildcard(actor: User) -> bool:
    return WILDCARD_PERMISSION in normalize_permissions(actor.permissions)


def _require_active_citizen(actor: User) -> None:
    if not actor.is_active:
        raise PermissionError("Требуется активная учётная запись гражданина Ratcraftia.")


def _refresh_expired_mandates(session: Session) -> None:
    now = utc_now()
    mandates = session.exec(
        select(DeputyMandate).where(DeputyMandate.status == "active")
    ).all()
    changed = False
    for mandate in mandates:
        if now >= _as_utc(mandate.ends_at):
            mandate.status = "expired"
            mandate.ended_at = now
            mandate.ended_reason = "term_expired"
            touch(mandate)
            session.add(mandate)
            changed = True
    if changed:
        session.commit()


def _require_active_deputy(session: Session, actor: User) -> None:
    _require_active_citizen(actor)
    if _has_wildcard(actor):
        return
    if not _is_active_deputy(session, actor.id):
        raise PermissionError("Парламентские действия доступны только действующим депутатам.")


def _bill_counts(session: Session, bill_id: int) -> tuple[int, int]:
    votes = session.exec(select(BillVote).where(BillVote.bill_id == bill_id)).all()
    yes_votes = sum(1 for vote in votes if vote.vote == "yes")
    no_votes = sum(1 for vote in votes if vote.vote == "no")
    return yes_votes, no_votes


def _referendum_counts(session: Session, referendum_id: int) -> tuple[int, int]:
    votes = session.exec(
        select(ReferendumVote).where(ReferendumVote.referendum_id == referendum_id)
    ).all()
    yes_votes = sum(1 for vote in votes if vote.vote == "yes")
    no_votes = sum(1 for vote in votes if vote.vote == "no")
    return yes_votes, no_votes


def _referendum_signature_count(session: Session, referendum_id: int) -> int:
    return len(
        session.exec(
            select(ReferendumSignature).where(ReferendumSignature.referendum_id == referendum_id)
        ).all()
    )


def _candidate_signature_count(session: Session, candidate_id: int) -> int:
    return len(
        session.exec(
            select(ParliamentCandidateSignature).where(
                ParliamentCandidateSignature.candidate_id == candidate_id
            )
        ).all()
    )


def _candidate_vote_count(session: Session, election_id: int, candidate_id: int) -> int:
    return len(
        session.exec(
            select(ParliamentElectionVote).where(
                ParliamentElectionVote.election_id == election_id,
                ParliamentElectionVote.candidate_id == candidate_id,
            )
        ).all()
    )


def _election_ballot_count(session: Session, election_id: int) -> int:
    votes = session.exec(
        select(ParliamentElectionVote).where(ParliamentElectionVote.election_id == election_id)
    ).all()
    return len({vote.voter_id for vote in votes})


def _refresh_bill_status(session: Session, bill: Bill) -> Bill:
    if bill.status == "enacted":
        return bill
    yes_votes, no_votes = _bill_counts(session, bill.id)
    total_votes = yes_votes + no_votes
    next_status = "open"
    if total_votes >= PARLIAMENT_QUORUM:
        next_status = "approved" if yes_votes > no_votes else "rejected"
    if bill.status != next_status:
        bill.status = next_status
        touch(bill)
        session.add(bill)
        session.commit()
        session.refresh(bill)
    return bill


def _refresh_referendum_status(session: Session, referendum: Referendum) -> Referendum:
    if referendum.status == "enacted":
        return referendum

    now = utc_now()
    changed = False
    signature_count = _referendum_signature_count(session, referendum.id)
    if referendum.status == "collecting_signatures" and signature_count >= referendum.required_signatures:
        referendum.status = "open"
        referendum.opens_at = now
        referendum.closes_at = now + timedelta(days=REFERENDUM_DURATION_DAYS)
        changed = True

    if referendum.status == "open" and now > _as_utc(referendum.closes_at):
        yes_votes, no_votes = _referendum_counts(session, referendum.id)
        total_votes = yes_votes + no_votes
        if total_votes < referendum.required_quorum:
            referendum.status = "failed_quorum"
        elif yes_votes > no_votes:
            referendum.status = "approved"
        else:
            referendum.status = "rejected"
        changed = True

    if changed:
        touch(referendum)
        session.add(referendum)
        session.commit()
        session.refresh(referendum)
    return referendum


def _update_candidate_status(session: Session, candidate: ParliamentCandidate) -> ParliamentCandidate:
    if candidate.status in {"elected", "not_elected"}:
        return candidate

    next_status = "collecting_signatures"
    if candidate.party_name.strip() or _candidate_signature_count(session, candidate.id) >= candidate.required_signatures:
        next_status = "registered"

    if candidate.status != next_status:
        candidate.status = next_status
        touch(candidate)
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
    return candidate


def _available_seat_numbers(session: Session) -> list[int]:
    occupied = {mandate.seat_number for mandate in _active_deputy_mandates(session)}
    return [seat for seat in range(1, PARLIAMENT_SEAT_COUNT + 1) if seat not in occupied]


def _finalize_parliament_election(
    session: Session,
    election: ParliamentElection,
) -> ParliamentElection:
    if election.status == "finalized":
        return election
    if election.status == "open" and utc_now() <= _as_utc(election.closes_at):
        return election

    now = utc_now()
    election.status = "closed"
    touch(election)
    session.add(election)

    active_mandates = _active_deputy_mandates(session)
    if election.kind == "general":
        seat_numbers = list(range(1, PARLIAMENT_SEAT_COUNT + 1))
        for mandate in active_mandates:
            mandate.status = "ended"
            mandate.ended_at = now
            mandate.ended_reason = "replaced_by_election"
            touch(mandate)
            session.add(mandate)
    else:
        seat_numbers = _available_seat_numbers(session)[: election.seat_count]

    candidates = session.exec(
        select(ParliamentCandidate).where(ParliamentCandidate.election_id == election.id)
    ).all()
    for candidate in candidates:
        _update_candidate_status(session, candidate)
    candidates = session.exec(
        select(ParliamentCandidate).where(ParliamentCandidate.election_id == election.id)
    ).all()

    ranked = sorted(
        [candidate for candidate in candidates if candidate.status == "registered"],
        key=lambda candidate: (
            -_candidate_vote_count(session, election.id, candidate.id),
            -_candidate_signature_count(session, candidate.id),
            candidate.created_at,
            candidate.id,
        ),
    )

    winner_ids: set[int] = set()
    seat_index = 0
    for candidate in ranked:
        if seat_index >= len(seat_numbers):
            break
        if _is_active_deputy(session, candidate.user_id):
            continue
        winner_ids.add(candidate.id)
        session.add(
            DeputyMandate(
                seat_number=seat_numbers[seat_index],
                deputy_id=candidate.user_id,
                election_id=election.id,
                status="active",
                starts_at=now,
                ends_at=_add_calendar_months(now, DEPUTY_TERM_MONTHS),
            )
        )
        seat_index += 1

    for candidate in candidates:
        candidate.status = "elected" if candidate.id in winner_ids else "not_elected"
        touch(candidate)
        session.add(candidate)

    election.status = "finalized"
    touch(election)
    session.add(election)
    session.commit()
    session.refresh(election)
    return election


def _ensure_open_parliament_election(session: Session, actor: User | None = None) -> ParliamentElection | None:
    _refresh_expired_mandates(session)

    open_elections = session.exec(
        select(ParliamentElection)
        .where(ParliamentElection.status == "open")
        .order_by(ParliamentElection.created_at.desc())
    ).all()
    for election in open_elections:
        if utc_now() > _as_utc(election.closes_at):
            _finalize_parliament_election(session, election)

    active_election = session.exec(
        select(ParliamentElection)
        .where(ParliamentElection.status == "open")
        .order_by(ParliamentElection.created_at.desc())
    ).first()
    if active_election:
        return active_election

    vacancies = len(_available_seat_numbers(session))
    if vacancies <= 0:
        return None

    created_at = utc_now()
    election = ParliamentElection(
        title=(
            "Общие выборы парламента Ratcraftia"
            if vacancies == PARLIAMENT_SEAT_COUNT
            else f"Дополнительные выборы на {vacancies} мест"
        ),
        kind="general" if vacancies == PARLIAMENT_SEAT_COUNT else "by_election",
        status="open",
        seat_count=vacancies,
        created_by_id=actor.id if actor else None,
        opens_at=created_at,
        closes_at=created_at + timedelta(days=PARLIAMENT_ELECTION_DURATION_DAYS),
    )
    session.add(election)
    session.commit()
    session.refresh(election)
    return election


def _resolve_user_identifier(session: Session, identifier: str | None) -> User | None:
    normalized = (identifier or "").strip()
    if not normalized:
        return None
    user = session.exec(select(User).where(User.uin == normalized)).first()
    if user:
        return user
    user = session.exec(select(User).where(User.login == normalized.lower())).first()
    if user:
        return user
    return session.exec(select(User).where(User.uan == normalized)).first()


def serialize_bill(session: Session, bill: Bill) -> BillRead:
    bill = _refresh_bill_status(session, bill)
    proposer = session.get(User, bill.proposer_id)
    yes_votes, no_votes = _bill_counts(session, bill.id)
    total_votes = yes_votes + no_votes
    return BillRead(
        id=bill.id,
        title=bill.title,
        summary=bill.summary,
        proposed_text=bill.proposed_text,
        law_id=bill.law_id,
        target_level=bill.target_level,
        status=bill.status,
        proposer_name=full_name(proposer) if proposer else "Неизвестно",
        created_at=bill.created_at,
        yes_votes=yes_votes,
        no_votes=no_votes,
        total_votes=total_votes,
        quorum_required=PARLIAMENT_QUORUM,
        quorum_reached=total_votes >= PARLIAMENT_QUORUM,
    )


def serialize_referendum(session: Session, referendum: Referendum) -> ReferendumRead:
    referendum = _refresh_referendum_status(session, referendum)
    proposer = session.get(User, referendum.proposer_id)
    subject = session.get(User, referendum.subject_user_id) if referendum.subject_user_id else None
    yes_votes, no_votes = _referendum_counts(session, referendum.id)
    total_votes = yes_votes + no_votes
    signature_count = _referendum_signature_count(session, referendum.id)
    return ReferendumRead(
        id=referendum.id,
        title=referendum.title,
        description=referendum.description,
        proposed_text=referendum.proposed_text,
        law_id=referendum.law_id,
        target_level=referendum.target_level,
        matter_type=referendum.matter_type,
        status=referendum.status,
        proposer_name=full_name(proposer) if proposer else "Неизвестно",
        subject_user_id=referendum.subject_user_id,
        subject_name=full_name(subject) if subject else None,
        opens_at=referendum.opens_at,
        closes_at=referendum.closes_at,
        created_at=referendum.created_at,
        signature_count=signature_count,
        required_signatures=referendum.required_signatures,
        yes_votes=yes_votes,
        no_votes=no_votes,
        total_votes=total_votes,
        required_quorum=referendum.required_quorum,
        quorum_reached=total_votes >= referendum.required_quorum,
    )


def serialize_parliament_candidate(
    session: Session,
    candidate: ParliamentCandidate,
) -> ParliamentCandidateRead:
    candidate = _update_candidate_status(session, candidate)
    user = session.get(User, candidate.user_id)
    return ParliamentCandidateRead(
        id=candidate.id,
        user_id=candidate.user_id,
        full_name=full_name(user) if user else "Неизвестно",
        party_name=candidate.party_name,
        status=candidate.status,
        signatures=_candidate_signature_count(session, candidate.id),
        required_signatures=candidate.required_signatures,
        votes=_candidate_vote_count(session, candidate.election_id, candidate.id),
    )


def serialize_parliament_election(
    session: Session,
    election: ParliamentElection,
) -> ParliamentElectionRead:
    election = _finalize_parliament_election(session, election)
    candidates = session.exec(
        select(ParliamentCandidate)
        .where(ParliamentCandidate.election_id == election.id)
        .order_by(ParliamentCandidate.created_at, ParliamentCandidate.id)
    ).all()
    serialized_candidates = [serialize_parliament_candidate(session, candidate) for candidate in candidates]
    return ParliamentElectionRead(
        id=election.id,
        title=election.title,
        kind=election.kind,
        status=election.status,
        seat_count=election.seat_count,
        opens_at=election.opens_at,
        closes_at=election.closes_at,
        created_at=election.created_at,
        total_ballots=_election_ballot_count(session, election.id),
        candidate_count=len(serialized_candidates),
        registered_candidate_count=sum(1 for candidate in serialized_candidates if candidate.status == "registered"),
        candidates=serialized_candidates,
    )


def serialize_parliament_summary(session: Session) -> ParliamentSummaryRead:
    active_election = _ensure_open_parliament_election(session)
    mandates = _active_deputy_mandates(session)
    deputies: list[DeputyRead] = []
    for mandate in mandates:
        deputy = session.get(User, mandate.deputy_id)
        deputies.append(
            DeputyRead(
                user_id=mandate.deputy_id,
                full_name=full_name(deputy) if deputy else "Неизвестно",
                seat_number=mandate.seat_number,
                starts_at=mandate.starts_at,
                ends_at=mandate.ends_at,
            )
        )
    return ParliamentSummaryRead(
        seat_count=PARLIAMENT_SEAT_COUNT,
        quorum=PARLIAMENT_QUORUM,
        vacancies=PARLIAMENT_SEAT_COUNT - len(deputies),
        deputies=deputies,
        active_election=serialize_parliament_election(session, active_election) if active_election else None,
    )


def serialize_law(law: Law) -> LawRead:
    return LawRead(
        id=law.id,
        title=law.title,
        slug=law.slug,
        level=law.level,
        version=law.version,
        status=law.status,
        adopted_via=law.adopted_via,
        current_text=law.current_text,
        updated_at=law.updated_at,
    )


def serialize_news(session: Session, news: NewsPost) -> NewsRead:
    author = session.get(User, news.author_id)
    return NewsRead(
        id=news.id,
        title=news.title,
        body=news.body,
        author_name=full_name(author) if author else "Неизвестно",
        created_at=news.created_at,
    )


def serialize_mail(session: Session, message: MailMessage) -> MailRead:
    sender = session.get(User, message.sender_id)
    recipient = session.get(User, message.recipient_id)
    return MailRead(
        id=message.id,
        from_address=message.from_address,
        to_address=message.to_address,
        subject=message.subject,
        text=message.text,
        sender_name=full_name(sender) if sender else "Неизвестно",
        recipient_name=full_name(recipient) if recipient else "Неизвестно",
        created_at=message.created_at,
        read_at=message.read_at,
    )


def resolve_mailbox(session: Session, address: str) -> User:
    normalized = address.strip()
    if normalized.lower().endswith("@citizen"):
        uin = normalized[:-8]
        user = session.exec(select(User).where(User.uin == uin)).first()
        if user:
            return user
    if normalized.lower().endswith("@fn"):
        login = normalized[:-3]
        user = session.exec(select(User).where(User.login == login)).first()
        if user:
            return user
    if normalized.lower().endswith("@gov"):
        local = normalized[:-4]
        parts = local.split(".", 1)
        if len(parts) == 2:
            initials, org_slug = parts
            users = session.exec(select(User).where(User.org_id.is_not(None))).all()
            for user in users:
                org = get_org(session, user)
                if org and org.slug.lower() == org_slug.lower() and initials_code(user).upper() == initials.upper():
                    return user
    raise ValueError("Адрес GovMail не найден.")


def send_mail(session: Session, actor: User, payload: MailCreate) -> MailRead:
    recipient = resolve_mailbox(session, payload.to)
    message = MailMessage(
        sender_id=actor.id,
        recipient_id=recipient.id,
        from_address=f"{actor.login}@fn",
        to_address=payload.to,
        subject=payload.subject.strip(),
        text=payload.text.strip(),
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    notify_users(
        session,
        [recipient.id],
        title="Новое GovMail письмо",
        body=f"{actor.login}@fn: {payload.subject.strip()}",
        url="/",
        tag="mail",
    )
    return serialize_mail(session, message)


def list_mail(session: Session, actor: User, box: str) -> list[MailRead]:
    if box == "sent":
        messages = session.exec(
            select(MailMessage).where(MailMessage.sender_id == actor.id).order_by(MailMessage.created_at.desc())
        ).all()
    else:
        messages = session.exec(
            select(MailMessage).where(MailMessage.recipient_id == actor.id).order_by(MailMessage.created_at.desc())
        ).all()
        changed = False
        for message in messages:
            if message.read_at is None:
                message.read_at = utc_now()
                changed = True
        if changed:
            session.commit()
    return [serialize_mail(session, message) for message in messages]


def post_news(session: Session, actor: User, payload: NewsCreate) -> NewsRead:
    require_permission(actor, NEWS_MANAGE_PERMISSION)
    news = NewsPost(title=payload.title.strip(), body=payload.body.strip(), author_id=actor.id)
    session.add(news)
    session.commit()
    session.refresh(news)
    notify_all_users(
        session,
        title="Новая новость Ratcraftia",
        body=news.title,
        url="/",
        tag="news",
        exclude_user_ids=[actor.id],
    )
    return serialize_news(session, news)


def delete_news(session: Session, actor: User, news_id: int) -> None:
    require_permission(actor, NEWS_MANAGE_PERMISSION)
    news = session.get(NewsPost, news_id)
    if not news:
        raise ValueError("Новость не найдена.")
    session.delete(news)
    session.commit()


def create_org(session: Session, actor: User, payload: OrganizationCreate) -> OrganizationRead:
    require_permission(actor, ORGS_CREATE_PERMISSION)
    if session.exec(select(Organization).where(Organization.slug == payload.slug)).first():
        raise ValueError("Организация с таким slug уже существует.")
    org = Organization(
        name=payload.name.strip(),
        slug=payload.slug.strip().lower(),
        kind=payload.kind.strip(),
        description=payload.description.strip(),
    )
    session.add(org)
    _record_admin_log(
        session,
        actor,
        action="organization.create",
        summary=f"Создана организация {org.name}",
        target_label=org.name,
    )
    session.commit()
    session.refresh(org)
    return serialize_org(org)


def create_user(session: Session, payload: UserCreate, actor: User | None = None) -> UserRead:
    if session.exec(select(User).where(User.uin == payload.uin)).first():
        raise ValueError("Пользователь с таким УИН уже существует.")
    if session.exec(select(User).where(User.uan == payload.uan)).first():
        raise ValueError("Пользователь с таким УАН уже существует.")
    if session.exec(select(User).where(User.login == payload.login.lower())).first():
        raise ValueError("Пользователь с таким логином уже существует.")
    org_id = None
    if payload.org_slug:
        org = session.exec(select(Organization).where(Organization.slug == payload.org_slug.lower())).first()
        if not org:
            raise ValueError("Организация не найдена.")
        org_id = org.id
    user = User(
        uin=payload.uin,
        uan=payload.uan,
        login=payload.login.lower(),
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        patronymic=payload.patronymic.strip(),
        password_hash=get_password_hash(payload.password),
        permissions=serialize_permissions(payload.permissions),
        org_id=org_id,
        position_title=payload.position_title.strip(),
        photo_url=payload.photo_url,
    )
    session.add(user)
    session.flush()
    if actor:
        _record_admin_log(
            session,
            actor,
            action="user.create",
            summary=f"Создан пользователь {full_name(user)}",
            target_user=user,
        )
    session.commit()
    session.refresh(user)
    return serialize_user(session, user, show_uan=True)


def update_user_identity(
    session: Session,
    actor: User,
    target: User,
    payload: UserUpdate,
) -> UserRead:
    require_permission(actor, USERS_UPDATE_PERMISSION)
    normalized_uin = payload.uin.strip()
    normalized_uan = payload.uan.strip()
    if actor.id == target.id and normalized_uin != target.uin:
        raise PermissionError("Собственный УИН нельзя менять из активной сессии.")
    if session.exec(select(User).where(User.uin == normalized_uin, User.id != target.id)).first():
        raise ValueError("Пользователь с таким УИН уже существует.")
    if session.exec(select(User).where(User.uan == normalized_uan, User.id != target.id)).first():
        raise ValueError("Пользователь с таким УАН уже существует.")

    changes: list[str] = []
    if target.uin != normalized_uin:
        changes.append("УИН")
    if target.uan != normalized_uan:
        changes.append("УАН")
    if target.first_name != payload.first_name.strip():
        changes.append("имя")
    if target.last_name != payload.last_name.strip():
        changes.append("фамилия")
    if target.patronymic != payload.patronymic.strip():
        changes.append("отчество")

    target.uin = normalized_uin
    target.uan = normalized_uan
    target.first_name = payload.first_name.strip()
    target.last_name = payload.last_name.strip()
    target.patronymic = payload.patronymic.strip()
    touch(target)
    session.add(target)

    if changes:
        _record_admin_log(
            session,
            actor,
            action="user.update",
            summary=f"Обновлены поля пользователя {full_name(target)}: {', '.join(changes)}",
            target_user=target,
        )
    session.commit()
    session.refresh(target)

    if changes:
        notify_users(
            session,
            [target.id],
            title="Данные профиля RGOV обновлены",
            body=f"Изменены поля: {', '.join(changes)}",
            url="/#admin",
            tag="user-update",
        )
    return serialize_user(session, target, show_uan=True)


def list_transfer_directory(session: Session) -> list[RatublesDirectoryEntryRead]:
    users = session.exec(
        select(User).where(User.is_active == True).order_by(User.last_name, User.first_name)  # noqa: E712
    ).all()
    organizations = session.exec(select(Organization).order_by(Organization.name)).all()
    return [serialize_user_directory(user) for user in users] + [
        serialize_org_directory(org) for org in organizations
    ]


def list_user_transactions(session: Session, actor: User) -> list[RatublesTransactionRead]:
    transactions = session.exec(
        select(RatublesTransaction)
        .where(
            (RatublesTransaction.sender_id == actor.id)
            | (RatublesTransaction.recipient_id == actor.id)
        )
        .order_by(RatublesTransaction.created_at.desc())
    ).all()
    return [
        serialize_ratubles_transaction(session, transaction, viewer_id=actor.id)
        for transaction in transactions
    ]


def list_all_transactions(session: Session, actor: User) -> list[RatublesTransactionRead]:
    require_permission(actor, ADMIN_LOGS_READ_PERMISSION)
    transactions = session.exec(
        select(RatublesTransaction).order_by(RatublesTransaction.created_at.desc())
    ).all()
    return [serialize_ratubles_transaction(session, transaction) for transaction in transactions]


def transfer_ratubles(
    session: Session,
    actor: User,
    payload: RatublesTransferRequest,
) -> RatublesTransactionRead:
    recipient, organization = _resolve_ratubles_recipient(
        session,
        payload.recipient_id,
        payload.recipient_kind,
    )
    if recipient and recipient.id == actor.id:
        raise ValueError("Нельзя отправить Ratubles самому себе.")
    if actor.ratubles < payload.amount:
        raise ValueError("Недостаточно Ratubles для перевода.")

    actor.ratubles -= payload.amount
    touch(actor)
    session.add(actor)

    if recipient:
        recipient.ratubles += payload.amount
        touch(recipient)
        session.add(recipient)
    elif organization:
        organization.ratubles += payload.amount
        touch(organization)
        session.add(organization)

    transaction = RatublesTransaction(
        kind="transfer",
        amount=payload.amount,
        reason=payload.reason.strip(),
        sender_id=actor.id,
        recipient_id=recipient.id if recipient else None,
        recipient_org_id=organization.id if organization else None,
        actor_id=actor.id,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    if recipient:
        notify_users(
            session,
            [recipient.id],
            title="Поступление Ratubles",
            body=f"{payload.amount} Ratubles от {full_name(actor)}",
            url="/#ratubles",
            tag="ratubles-transfer",
        )
    return serialize_ratubles_transaction(session, transaction, viewer_id=actor.id)


def mint_ratubles(
    session: Session,
    actor: User,
    payload: RatublesMintRequest,
) -> RatublesTransactionRead:
    require_permission(actor, RATUBLES_MINT_PERMISSION)
    recipient, organization = _resolve_ratubles_recipient(
        session,
        payload.recipient_id,
        payload.recipient_kind,
    )

    if recipient:
        recipient.ratubles += payload.amount
        touch(recipient)
        session.add(recipient)
        target_summary = f"Начислено {payload.amount} Ratubles пользователю {full_name(recipient)}"
    elif organization:
        organization.ratubles += payload.amount
        touch(organization)
        session.add(organization)
        target_summary = f"Начислено {payload.amount} Ratubles организации {organization.name}"
    else:
        raise ValueError("Получатель не найден.")

    transaction = RatublesTransaction(
        kind="mint",
        amount=payload.amount,
        reason=payload.reason.strip(),
        sender_id=None,
        recipient_id=recipient.id if recipient else None,
        recipient_org_id=organization.id if organization else None,
        actor_id=actor.id,
    )
    session.add(transaction)
    session.flush()
    _record_admin_log(
        session,
        actor,
        action="ratubles.mint",
        summary=target_summary,
        target_user=recipient,
        target_label=organization.name if organization else "",
        reason=payload.reason,
    )
    session.commit()
    session.refresh(transaction)

    if recipient:
        notify_users(
            session,
            [recipient.id],
            title="Начисление Ratubles",
            body=f"Начислено {payload.amount} Ratubles",
            url="/#ratubles",
            tag="ratubles-mint",
        )
    return serialize_ratubles_transaction(session, transaction)


def list_admin_logs(session: Session, actor: User) -> list[AdminLogRead]:
    require_permission(actor, ADMIN_LOGS_READ_PERMISSION)
    entries = session.exec(select(AdminLog).order_by(AdminLog.created_at.desc())).all()
    return [serialize_admin_log(session, entry) for entry in entries]


def change_user_permissions(
    session: Session,
    actor: User,
    target: User,
    permissions: list[str],
) -> UserRead:
    require_permission(
        actor,
        USER_PERMISSIONS_WRITE_PERMISSION,
        error_message="Только администратор может менять права доступа.",
    )
    target.permissions = serialize_permissions(permissions)
    touch(target)
    session.add(target)
    _record_admin_log(
        session,
        actor,
        action="user.permissions",
        summary=f"Обновлены права пользователя {full_name(target)}",
        target_user=target,
    )
    session.commit()
    session.refresh(target)
    notify_users(
        session,
        [target.id],
        title="Права доступа в RGOV обновлены",
        body=f"Новый уровень доступа: {permissions_label(target.permissions)}",
        url="/",
        tag="permissions",
    )
    return serialize_user(session, target, show_uan=True)


def hire_user(session: Session, actor: User, target: User, payload: HireRequest) -> UserRead:
    require_permission(actor, PERSONNEL_MANAGE_PERMISSION)
    org = session.exec(select(Organization).where(Organization.slug == payload.org_slug.lower())).first()
    if not org:
        raise ValueError("Организация не найдена.")
    target.org_id = org.id
    target.position_title = payload.position_title.strip()
    touch(target)
    session.add(target)
    _record_admin_log(
        session,
        actor,
        action="user.hire",
        summary=f"{full_name(target)} назначен в {org.name}",
        target_user=target,
        target_label=org.name,
    )
    session.commit()
    session.refresh(target)
    notify_users(
        session,
        [target.id],
        title="Назначение в орган Ratcraftia",
        body=f"{org.name}: {target.position_title}",
        url="/",
        tag="personnel",
    )
    return serialize_user(session, target)


def fire_user(session: Session, actor: User, target: User) -> UserRead:
    require_permission(actor, PERSONNEL_MANAGE_PERMISSION)
    org = get_org(session, target)
    target.org_id = None
    target.position_title = "Гражданин"
    if normalize_permissions(target.permissions) == PRESET_PERMISSIONS["government_staff"]:
        target.permissions = serialize_permissions([])
    touch(target)
    session.add(target)
    _record_admin_log(
        session,
        actor,
        action="user.fire",
        summary=f"{full_name(target)} переведён в гражданский статус",
        target_user=target,
        target_label=org.name if org else "",
    )
    session.commit()
    session.refresh(target)
    notify_users(
        session,
        [target.id],
        title="Статус занятости обновлён",
        body=f"Организация: {org.name if org else 'RGOV'}. Вы переведены в статус гражданина.",
        url="/",
        tag="personnel",
    )
    return serialize_user(session, target)


def change_login(session: Session, actor: User, new_login: str) -> ProfileResponse:
    normalized = new_login.lower().strip()
    if session.exec(select(User).where(User.login == normalized, User.id != actor.id)).first():
        raise ValueError("Такой логин уже занят.")
    if actor.login_changed_at and _local_date(actor.login_changed_at) == _local_date(utc_now()):
        raise ValueError("Логин можно менять только один раз в сутки.")
    actor.login = normalized
    actor.login_changed_at = utc_now()
    touch(actor)
    session.add(actor)
    session.commit()
    session.refresh(actor)
    return serialize_profile(session, actor)


def change_password(
    session: Session,
    actor: User,
    payload: PasswordChangeRequest,
) -> None:
    if not verify_password(payload.current_password, actor.password_hash):
        raise PermissionError("Текущий пароль указан неверно.")
    if payload.current_password == payload.new_password:
        raise ValueError("Новый пароль должен отличаться от текущего.")
    actor.password_hash = get_password_hash(payload.new_password)
    touch(actor)
    session.add(actor)
    session.commit()


def _apply_law_change(
    session: Session,
    *,
    title: str,
    target_level: str,
    proposed_text: str,
    adopted_via: str,
    actor: User,
    law_id: int | None,
    source_bill_id: int | None = None,
    source_referendum_id: int | None = None,
) -> Law:
    if law_id:
        law = session.get(Law, law_id)
        if not law:
            raise ValueError("Целевой закон не найден.")
        law.title = title.strip() or law.title
        law.level = target_level
        law.current_text = proposed_text.strip()
        law.version += 1
        law.adopted_via = adopted_via
        law.author_id = actor.id
        law.source_bill_id = source_bill_id
        law.source_referendum_id = source_referendum_id
        touch(law)
        session.add(law)
        session.commit()
        session.refresh(law)
        return law

    slug = ensure_unique_slug(session, slugify(title))
    law = Law(
        title=title.strip(),
        slug=slug,
        level=target_level,
        current_text=proposed_text.strip(),
        adopted_via=adopted_via,
        author_id=actor.id,
        source_bill_id=source_bill_id,
        source_referendum_id=source_referendum_id,
    )
    session.add(law)
    session.commit()
    session.refresh(law)
    return law


def list_parliament_elections(session: Session) -> list[ParliamentElectionRead]:
    _ensure_open_parliament_election(session)
    elections = session.exec(
        select(ParliamentElection).order_by(ParliamentElection.created_at.desc())
    ).all()
    return [serialize_parliament_election(session, election) for election in elections]


def nominate_parliament_candidate(
    session: Session,
    actor: User,
    election_id: int,
    payload: ParliamentCandidateCreate,
) -> ParliamentElectionRead:
    _require_active_citizen(actor)
    if _is_active_deputy(session, actor.id):
        raise ValueError("Действующий депутат не может одновременно выдвигаться на свободное место.")

    election = session.get(ParliamentElection, election_id)
    if not election:
        raise ValueError("Парламентские выборы не найдены.")
    election = _finalize_parliament_election(session, election)
    if election.status != "open":
        raise ValueError("Приём кандидатов по этим выборам уже завершён.")

    existing = session.exec(
        select(ParliamentCandidate).where(
            ParliamentCandidate.election_id == election_id,
            ParliamentCandidate.user_id == actor.id,
        )
    ).first()
    if existing:
        raise ValueError("Вы уже выдвинуты на этих выборах.")

    candidate = ParliamentCandidate(
        election_id=election_id,
        user_id=actor.id,
        party_name=payload.party_name.strip(),
        required_signatures=_signature_requirement(session),
        status="registered" if payload.party_name.strip() else "collecting_signatures",
    )
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    if not candidate.party_name.strip():
        session.add(ParliamentCandidateSignature(candidate_id=candidate.id, signer_id=actor.id))
        session.commit()
        _update_candidate_status(session, candidate)

    return serialize_parliament_election(session, election)


def sign_parliament_candidate(
    session: Session,
    actor: User,
    election_id: int,
    candidate_id: int,
) -> ParliamentElectionRead:
    _require_active_citizen(actor)
    election = session.get(ParliamentElection, election_id)
    if not election:
        raise ValueError("Парламентские выборы не найдены.")
    election = _finalize_parliament_election(session, election)
    if election.status != "open":
        raise ValueError("Сбор подписей по этим выборам уже завершён.")

    candidate = session.get(ParliamentCandidate, candidate_id)
    if not candidate or candidate.election_id != election_id:
        raise ValueError("Кандидат не найден.")

    record = session.exec(
        select(ParliamentCandidateSignature).where(
            ParliamentCandidateSignature.candidate_id == candidate_id,
            ParliamentCandidateSignature.signer_id == actor.id,
        )
    ).first()
    if record:
        raise ValueError("Ваша подпись уже учтена.")

    session.add(ParliamentCandidateSignature(candidate_id=candidate_id, signer_id=actor.id))
    session.commit()
    _update_candidate_status(session, candidate)
    return serialize_parliament_election(session, election)


def vote_parliament_candidate(
    session: Session,
    actor: User,
    election_id: int,
    candidate_id: int,
    vote: str,
) -> ParliamentElectionRead:
    _require_active_citizen(actor)
    election = session.get(ParliamentElection, election_id)
    if not election:
        raise ValueError("Парламентские выборы не найдены.")
    election = _finalize_parliament_election(session, election)
    if election.status != "open":
        raise ValueError("Голосование по этим выборам уже завершено.")

    candidate = session.get(ParliamentCandidate, candidate_id)
    if not candidate or candidate.election_id != election_id:
        raise ValueError("Кандидат не найден.")
    candidate = _update_candidate_status(session, candidate)
    if candidate.status != "registered":
        raise ValueError("Сначала кандидат должен собрать необходимое число подписей.")

    record = session.exec(
        select(ParliamentElectionVote).where(
            ParliamentElectionVote.election_id == election_id,
            ParliamentElectionVote.voter_id == actor.id,
            ParliamentElectionVote.candidate_id == candidate_id,
        )
    ).first()
    current_votes = session.exec(
        select(ParliamentElectionVote).where(
            ParliamentElectionVote.election_id == election_id,
            ParliamentElectionVote.voter_id == actor.id,
        )
    ).all()

    if vote == "yes":
        if not record and len(current_votes) >= election.seat_count:
            raise ValueError(
                f"Один избиратель может поддержать не более {election.seat_count} кандидатов."
            )
        if not record:
            session.add(
                ParliamentElectionVote(
                    election_id=election_id,
                    voter_id=actor.id,
                    candidate_id=candidate_id,
                )
            )
            session.commit()
    else:
        if record:
            session.delete(record)
            session.commit()

    return serialize_parliament_election(session, election)


def create_bill(session: Session, actor: User, payload: BillCreate) -> BillRead:
    _require_active_deputy(session, actor)
    if payload.target_level == "constitution":
        raise ValueError("Конституцию можно менять только через референдум.")
    bill = Bill(
        title=payload.title.strip(),
        summary=payload.summary.strip(),
        proposed_text=payload.proposed_text.strip(),
        law_id=payload.law_id,
        target_level=payload.target_level,
        proposer_id=actor.id,
        status="open",
    )
    session.add(bill)
    session.commit()
    session.refresh(bill)
    notify_all_users(
        session,
        title="Новый законопроект",
        body=bill.title,
        url="/",
        tag="bill",
        exclude_user_ids=[actor.id],
    )
    return serialize_bill(session, bill)


def vote_bill(session: Session, actor: User, bill_id: int, vote: str) -> BillRead:
    _require_active_deputy(session, actor)
    bill = session.get(Bill, bill_id)
    if not bill:
        raise ValueError("Законопроект не найден.")
    bill = _refresh_bill_status(session, bill)
    if bill.status == "enacted":
        raise ValueError("Законопроект уже принят.")

    record = session.exec(
        select(BillVote).where(BillVote.bill_id == bill_id, BillVote.voter_id == actor.id)
    ).first()
    if record:
        record.vote = vote
    else:
        record = BillVote(bill_id=bill_id, voter_id=actor.id, vote=vote)
    session.add(record)
    session.commit()
    session.refresh(bill)
    return serialize_bill(session, bill)


def publish_bill(session: Session, actor: User, bill_id: int) -> LawRead:
    _require_active_deputy(session, actor)
    bill = session.get(Bill, bill_id)
    if not bill:
        raise ValueError("Законопроект не найден.")
    bill = _refresh_bill_status(session, bill)
    if bill.status != "approved":
        if bill.status == "open":
            raise ValueError(
                f"Для публикации нужен кворум не менее {PARLIAMENT_QUORUM} депутатов и большинство голосов 'за'."
            )
        raise ValueError("Законопроект не получил парламентского большинства.")

    law = _apply_law_change(
        session,
        title=bill.title,
        target_level=bill.target_level,
        proposed_text=bill.proposed_text,
        adopted_via="parliament",
        actor=actor,
        law_id=bill.law_id,
        source_bill_id=bill.id,
    )
    bill.status = "enacted"
    touch(bill)
    session.add(bill)
    session.commit()
    return serialize_law(law)


def sign_referendum(session: Session, actor: User, referendum_id: int) -> ReferendumRead:
    _require_active_citizen(actor)
    referendum = session.get(Referendum, referendum_id)
    if not referendum:
        raise ValueError("Референдум не найден.")
    referendum = _refresh_referendum_status(session, referendum)
    if referendum.status != "collecting_signatures":
        raise ValueError("Сбор подписей по этому референдуму уже завершён.")

    record = session.exec(
        select(ReferendumSignature).where(
            ReferendumSignature.referendum_id == referendum_id,
            ReferendumSignature.signer_id == actor.id,
        )
    ).first()
    if record:
        raise ValueError("Ваша подпись уже учтена.")

    session.add(ReferendumSignature(referendum_id=referendum_id, signer_id=actor.id))
    session.commit()
    return serialize_referendum(session, referendum)


def create_referendum(session: Session, actor: User, payload: ReferendumCreate) -> ReferendumRead:
    _require_active_citizen(actor)

    matter_type = payload.matter_type.strip().lower()
    target_level = payload.target_level.strip().lower()
    subject = _resolve_user_identifier(session, payload.subject_identifier)

    if matter_type == "constitution_amendment":
        target_level = "constitution"
    elif matter_type in {"deputy_recall", "official_recall"}:
        target_level = "resolution"
        if not subject:
            raise ValueError("Для вопроса об отзыве нужно указать логин, УИН или УАН должностного лица.")
    elif matter_type == "government_question":
        target_level = "resolution"
    elif target_level == "constitution":
        raise ValueError("Изменение конституции должно оформляться как конституционная поправка.")

    if matter_type == "deputy_recall" and subject and not _is_active_deputy(session, subject.id):
        raise ValueError("Указанный гражданин сейчас не является действующим депутатом.")
    if matter_type == "official_recall" and subject and not subject.org_id and not subject.position_title.strip():
        raise ValueError("Указанный гражданин не занимает государственную должность.")

    now = utc_now()
    referendum = Referendum(
        title=payload.title.strip(),
        description=payload.description.strip(),
        proposed_text=payload.proposed_text.strip(),
        law_id=payload.law_id,
        target_level=target_level,
        matter_type=matter_type,
        proposer_id=actor.id,
        subject_user_id=subject.id if subject else None,
        required_signatures=_signature_requirement(session),
        required_quorum=_referendum_quorum_requirement(session),
        opens_at=now,
        closes_at=now,
        status="collecting_signatures",
    )
    session.add(referendum)
    session.commit()
    session.refresh(referendum)

    session.add(ReferendumSignature(referendum_id=referendum.id, signer_id=actor.id))
    session.commit()

    notify_all_users(
        session,
        title="Новая инициатива референдума",
        body=referendum.title,
        url="/",
        tag="referendum",
        exclude_user_ids=[actor.id],
    )
    return serialize_referendum(session, referendum)


def vote_referendum(session: Session, actor: User, referendum_id: int, vote: str) -> ReferendumRead:
    _require_active_citizen(actor)
    referendum = session.get(Referendum, referendum_id)
    if not referendum:
        raise ValueError("Референдум не найден.")
    referendum = _refresh_referendum_status(session, referendum)
    if referendum.status == "enacted":
        raise ValueError("Референдум уже исполнен.")
    if referendum.status == "collecting_signatures":
        raise ValueError("Сначала инициатива должна собрать необходимые подписи.")
    if referendum.status != "open":
        raise ValueError("Голосование по референдуму уже завершено.")

    record = session.exec(
        select(ReferendumVote).where(
            ReferendumVote.referendum_id == referendum_id,
            ReferendumVote.voter_id == actor.id,
        )
    ).first()
    if record:
        record.vote = vote
    else:
        record = ReferendumVote(referendum_id=referendum_id, voter_id=actor.id, vote=vote)
    session.add(record)
    session.commit()
    return serialize_referendum(session, referendum)


def publish_referendum(session: Session, actor: User, referendum_id: int) -> ReferendumOutcomeRead:
    _require_active_citizen(actor)
    referendum = session.get(Referendum, referendum_id)
    if not referendum:
        raise ValueError("Референдум не найден.")
    referendum = _refresh_referendum_status(session, referendum)
    if referendum.status != "approved":
        raise ValueError("Итог референдума ещё не одобрен и не может быть опубликован.")

    law: Law | None = None
    detail = "Итог референдума опубликован."

    if referendum.matter_type in {"constitution_amendment", "law_change", "government_question"}:
        law_id = referendum.law_id
        if referendum.target_level == "constitution" and law_id is None:
            constitution = session.exec(select(Law).where(Law.level == "constitution")).first()
            law_id = constitution.id if constitution else None
        law = _apply_law_change(
            session,
            title=referendum.title,
            target_level=referendum.target_level,
            proposed_text=referendum.proposed_text,
            adopted_via="referendum",
            actor=actor,
            law_id=law_id,
            source_referendum_id=referendum.id,
        )
    elif referendum.matter_type == "deputy_recall":
        mandates = session.exec(
            select(DeputyMandate).where(
                DeputyMandate.deputy_id == referendum.subject_user_id,
                DeputyMandate.status == "active",
            )
        ).all()
        if not mandates:
            raise ValueError("У указанного депутата нет активного мандата.")
        for mandate in mandates:
            mandate.status = "ended"
            mandate.ended_at = utc_now()
            mandate.ended_reason = "referendum_recall"
            touch(mandate)
            session.add(mandate)
        detail = "Полномочия депутата прекращены по итогам референдума."
    elif referendum.matter_type == "official_recall":
        subject = session.get(User, referendum.subject_user_id) if referendum.subject_user_id else None
        if not subject:
            raise ValueError("Должностное лицо не найдено.")
        subject.org_id = None
        subject.position_title = "Гражданин"
        touch(subject)
        session.add(subject)
        detail = "Должностное лицо освобождено от государственной должности."

    referendum.status = "enacted"
    touch(referendum)
    session.add(referendum)
    session.commit()
    session.refresh(referendum)
    return ReferendumOutcomeRead(
        referendum=serialize_referendum(session, referendum),
        law=serialize_law(law) if law else None,
        detail=detail,
    )
