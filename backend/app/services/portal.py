from __future__ import annotations

from datetime import timedelta, timezone
import re
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from ..core.config import get_settings
from ..core.security import get_password_hash
from ..models import (
    AdminLog,
    Bill,
    BillVote,
    Law,
    MailMessage,
    NewsPost,
    Organization,
    RatublesTransaction,
    Referendum,
    ReferendumVote,
    User,
    utc_now,
)
from ..schemas import (
    AdminLogRead,
    BillCreate,
    BillRead,
    HireRequest,
    LawRead,
    MailCreate,
    MailRead,
    NewsCreate,
    NewsRead,
    OrganizationCreate,
    OrganizationRead,
    ProfileResponse,
    RatublesMintRequest,
    RatublesTransactionRead,
    RatublesTransferRequest,
    ReferendumCreate,
    ReferendumRead,
    UserCreate,
    UserDirectoryRead,
    UserRead,
    UserUpdate,
)
from .notifications import notify_all_users, notify_users
from .permissions import (
    ADMIN_LOGS_READ_PERMISSION,
    BILLS_MANAGE_PERMISSION,
    NEWS_MANAGE_PERMISSION,
    ORGS_CREATE_PERMISSION,
    PERSONNEL_MANAGE_PERMISSION,
    PRESET_PERMISSIONS,
    RATUBLES_MINT_PERMISSION,
    REFERENDA_MANAGE_PERMISSION,
    USERS_UPDATE_PERMISSION,
    USER_PERMISSIONS_WRITE_PERMISSION,
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
    )


def serialize_profile(session: Session, user: User) -> ProfileResponse:
    return ProfileResponse(**serialize_user(session, user, show_uan=True).model_dump())


def serialize_user_directory(user: User) -> UserDirectoryRead:
    return UserDirectoryRead(
        id=user.id,
        uin=user.uin,
        login=user.login,
        full_name=full_name(user),
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
    recipient = session.get(User, transaction.recipient_id)
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
        sender_name=full_name(sender) if sender else None,
        sender_uin=sender.uin if sender else None,
        recipient_name=full_name(recipient) if recipient else None,
        recipient_uin=recipient.uin if recipient else None,
        actor_name=full_name(actor) if actor else None,
        created_at=transaction.created_at,
    )


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


def serialize_bill(session: Session, bill: Bill) -> BillRead:
    proposer = session.get(User, bill.proposer_id)
    yes_votes, no_votes = _bill_counts(session, bill.id)
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
    )


def serialize_referendum(session: Session, referendum: Referendum) -> ReferendumRead:
    proposer = session.get(User, referendum.proposer_id)
    yes_votes, no_votes = _referendum_counts(session, referendum.id)
    return ReferendumRead(
        id=referendum.id,
        title=referendum.title,
        description=referendum.description,
        proposed_text=referendum.proposed_text,
        law_id=referendum.law_id,
        target_level=referendum.target_level,
        status=referendum.status,
        proposer_name=full_name(proposer) if proposer else "Неизвестно",
        opens_at=referendum.opens_at,
        closes_at=referendum.closes_at,
        created_at=referendum.created_at,
        yes_votes=yes_votes,
        no_votes=no_votes,
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


def list_transfer_directory(session: Session) -> list[UserDirectoryRead]:
    users = session.exec(
        select(User).where(User.is_active == True).order_by(User.last_name, User.first_name)  # noqa: E712
    ).all()
    return [serialize_user_directory(user) for user in users]


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
    recipient = session.get(User, payload.recipient_id)
    if not recipient or not recipient.is_active:
        raise ValueError("Получатель не найден.")
    if recipient.id == actor.id:
        raise ValueError("Нельзя отправить Ratubles самому себе.")
    if actor.ratubles < payload.amount:
        raise ValueError("Недостаточно Ratubles для перевода.")

    actor.ratubles -= payload.amount
    recipient.ratubles += payload.amount
    touch(actor)
    touch(recipient)
    session.add(actor)
    session.add(recipient)

    transaction = RatublesTransaction(
        kind="transfer",
        amount=payload.amount,
        reason=payload.reason.strip(),
        sender_id=actor.id,
        recipient_id=recipient.id,
        actor_id=actor.id,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

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
    recipient = session.get(User, payload.recipient_id)
    if not recipient or not recipient.is_active:
        raise ValueError("Получатель не найден.")

    recipient.ratubles += payload.amount
    touch(recipient)
    session.add(recipient)

    transaction = RatublesTransaction(
        kind="mint",
        amount=payload.amount,
        reason=payload.reason.strip(),
        sender_id=None,
        recipient_id=recipient.id,
        actor_id=actor.id,
    )
    session.add(transaction)
    session.flush()
    _record_admin_log(
        session,
        actor,
        action="ratubles.mint",
        summary=f"Начислено {payload.amount} Ratubles пользователю {full_name(recipient)}",
        target_user=recipient,
        reason=payload.reason,
    )
    session.commit()
    session.refresh(transaction)

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


def create_bill(session: Session, actor: User, payload: BillCreate) -> BillRead:
    require_permission(actor, BILLS_MANAGE_PERMISSION)
    if payload.target_level == "constitution":
        raise ValueError("Конституцию можно менять только через референдум.")
    bill = Bill(
        title=payload.title.strip(),
        summary=payload.summary.strip(),
        proposed_text=payload.proposed_text.strip(),
        law_id=payload.law_id,
        target_level=payload.target_level,
        proposer_id=actor.id,
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
    require_permission(actor, BILLS_MANAGE_PERMISSION)
    bill = session.get(Bill, bill_id)
    if not bill:
        raise ValueError("Законопроект не найден.")
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
    yes_votes, no_votes = _bill_counts(session, bill_id)
    if vote == "yes":
        yes_votes += 0
    if yes_votes > no_votes:
        bill.status = "approved"
    elif no_votes >= yes_votes and yes_votes + no_votes > 0:
        bill.status = "rejected"
    touch(bill)
    session.add(bill)
    session.commit()
    session.refresh(bill)
    return serialize_bill(session, bill)


def publish_bill(session: Session, actor: User, bill_id: int) -> LawRead:
    require_permission(actor, BILLS_MANAGE_PERMISSION)
    bill = session.get(Bill, bill_id)
    if not bill:
        raise ValueError("Законопроект не найден.")
    yes_votes, no_votes = _bill_counts(session, bill_id)
    if yes_votes <= no_votes:
        raise ValueError("Для публикации нужно парламентское большинство голосов 'за'.")
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


def create_referendum(session: Session, actor: User, payload: ReferendumCreate) -> ReferendumRead:
    require_permission(actor, REFERENDA_MANAGE_PERMISSION)
    referendum = Referendum(
        title=payload.title.strip(),
        description=payload.description.strip(),
        proposed_text=payload.proposed_text.strip(),
        law_id=payload.law_id,
        target_level=payload.target_level,
        proposer_id=actor.id,
        closes_at=utc_now() + timedelta(days=payload.closes_in_days),
    )
    session.add(referendum)
    session.commit()
    session.refresh(referendum)
    notify_all_users(
        session,
        title="Новый референдум",
        body=referendum.title,
        url="/",
        tag="referendum",
        exclude_user_ids=[actor.id],
    )
    return serialize_referendum(session, referendum)


def vote_referendum(session: Session, actor: User, referendum_id: int, vote: str) -> ReferendumRead:
    referendum = session.get(Referendum, referendum_id)
    if not referendum:
        raise ValueError("Референдум не найден.")
    if referendum.status == "enacted":
        raise ValueError("Референдум уже завершён.")
    if utc_now() > _as_utc(referendum.closes_at):
        referendum.status = "closed"
        touch(referendum)
        session.add(referendum)
        session.commit()
        raise ValueError("Голосование по референдуму уже закрыто.")
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
    yes_votes, no_votes = _referendum_counts(session, referendum_id)
    if yes_votes > no_votes:
        referendum.status = "approved"
    elif no_votes >= yes_votes and yes_votes + no_votes > 0:
        referendum.status = "rejected"
    touch(referendum)
    session.add(referendum)
    session.commit()
    session.refresh(referendum)
    return serialize_referendum(session, referendum)


def publish_referendum(session: Session, actor: User, referendum_id: int) -> LawRead:
    require_permission(actor, REFERENDA_MANAGE_PERMISSION)
    referendum = session.get(Referendum, referendum_id)
    if not referendum:
        raise ValueError("Референдум не найден.")
    yes_votes, no_votes = _referendum_counts(session, referendum_id)
    if yes_votes <= no_votes:
        raise ValueError("Для публикации нужен положительный итог референдума.")
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
    referendum.status = "enacted"
    touch(referendum)
    session.add(referendum)
    session.commit()
    return serialize_law(law)
