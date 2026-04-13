from __future__ import annotations

import argparse
import sys

from sqlmodel import Session, select

from .db import get_engine, init_db
from .models import User
from .schemas import BillCreate, HireRequest, MailCreate, NewsCreate, OrganizationCreate, ReferendumCreate, UserCreate
from .services.bootstrap import seed_demo_data
from .services.permissions import permissions_label
from .services.portal import (
    change_user_permissions,
    create_bill,
    delete_news,
    create_org,
    create_user,
    fire_user,
    full_name,
    hire_user,
    post_news,
    publish_bill,
    publish_referendum,
    send_mail,
    vote_bill,
    vote_referendum,
)


def _open_session() -> Session:
    init_db()
    session = Session(get_engine())
    seed_demo_data(session)
    return session


def _get_user_by_uin(session: Session, uin: str) -> User:
    user = session.exec(select(User).where(User.uin == uin)).first()
    if not user:
        raise SystemExit(f"Пользователь с УИН {uin} не найден.")
    return user


def _print_title(title: str) -> None:
    print(f"\n=== {title} ===")


def cmd_seed_demo(_: argparse.Namespace) -> None:
    with _open_session():
        pass
    print("Демо-данные RGOV готовы.")


def cmd_list_users(_: argparse.Namespace) -> None:
    with _open_session() as session:
        _print_title("Пользователи")
        for user in session.exec(select(User).order_by(User.last_name, User.first_name)).all():
            print(
                f"{user.uin} | {user.login} | {full_name(user)} | "
                f"{permissions_label(user.permissions)} | {user.permissions or '-'}"
            )


def cmd_create_user(args: argparse.Namespace) -> None:
    with _open_session() as session:
        user = create_user(
            session,
            UserCreate(
                uin=args.uin,
                uan=args.uan,
                login=args.login,
                password=args.password,
                first_name=args.first_name,
                last_name=args.last_name,
                patronymic=args.patronymic,
                permissions=args.permissions,
                org_slug=args.org_slug,
                position_title=args.position_title,
                photo_url=args.photo_url,
            ),
        )
        print(f"Создан пользователь: {user.full_name} ({user.uin})")


def cmd_post_news(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        news = post_news(session, actor, NewsCreate(title=args.title, body=args.body))
        print(f"Новость опубликована: {news.id} | {news.title}")


def cmd_delete_news(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        delete_news(session, actor, args.news_id)
        print(f"Новость {args.news_id} удалена пользователем {actor.login}.")


def cmd_create_org(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        org = create_org(
            session,
            actor,
            OrganizationCreate(
                name=args.name,
                slug=args.slug,
                kind=args.kind,
                description=args.description,
            ),
        )
        print(f"Создана организация: {org.name} ({org.slug})")


def cmd_change_permissions(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        target = _get_user_by_uin(session, args.target_uin)
        user = change_user_permissions(session, actor, target, args.permissions)
        print(
            f"Права доступа обновлены: {user.full_name} -> "
            f"{', '.join(user.permissions) if user.permissions else 'нет'}"
        )


def cmd_hire(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        target = _get_user_by_uin(session, args.target_uin)
        user = hire_user(
            session,
            actor,
            target,
            HireRequest(org_slug=args.org_slug, position_title=args.position_title),
        )
        print(f"Пользователь назначен: {user.full_name} -> {user.position_title}")


def cmd_fire(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        target = _get_user_by_uin(session, args.target_uin)
        user = fire_user(session, actor, target)
        print(f"Пользователь уволен: {user.full_name}")


def cmd_create_bill(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        bill = create_bill(
            session,
            actor,
            BillCreate(
                title=args.title,
                summary=args.summary,
                proposed_text=args.text,
                law_id=args.law_id,
                target_level="law",
            ),
        )
        print(f"Создан законопроект #{bill.id}: {bill.title}")


def cmd_vote_bill(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        bill = vote_bill(session, actor, args.bill_id, args.vote)
        print(f"Голос учтён. Законопроект #{bill.id}: {bill.yes_votes} за / {bill.no_votes} против")


def cmd_publish_bill(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        law = publish_bill(session, actor, args.bill_id)
        print(f"Закон опубликован: {law.title} v{law.version}")


def cmd_create_referendum(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        referendum = create_referendum(
            session,
            actor,
            ReferendumCreate(
                title=args.title,
                description=args.description,
                proposed_text=args.text,
                law_id=args.law_id,
                target_level=args.target_level,
                closes_in_days=args.closes_in_days,
            ),
        )
        print(f"Создан референдум #{referendum.id}: {referendum.title}")


def cmd_vote_referendum(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        referendum = vote_referendum(session, actor, args.referendum_id, args.vote)
        print(
            f"Голос учтён. Референдум #{referendum.id}: "
            f"{referendum.yes_votes} за / {referendum.no_votes} против"
        )


def cmd_publish_referendum(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        law = publish_referendum(session, actor, args.referendum_id)
        print(f"Результат референдума опубликован: {law.title} v{law.version}")


def cmd_send_mail(args: argparse.Namespace) -> None:
    with _open_session() as session:
        actor = _get_user_by_uin(session, args.actor_uin)
        message = send_mail(
            session,
            actor,
            MailCreate(to=args.to, subject=args.subject, text=args.text),
        )
        print(f"Сообщение отправлено: {message.to_address} | {message.subject}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="RCS",
        description="Ratcraftia Control Script",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("seed-demo").set_defaults(func=cmd_seed_demo)
    subparsers.add_parser("list-users").set_defaults(func=cmd_list_users)

    create_user_parser = subparsers.add_parser("create-user")
    create_user_parser.add_argument("--uin", required=True)
    create_user_parser.add_argument("--uan", required=True)
    create_user_parser.add_argument("--login", required=True)
    create_user_parser.add_argument("--password", required=True)
    create_user_parser.add_argument("--first-name", required=True)
    create_user_parser.add_argument("--last-name", required=True)
    create_user_parser.add_argument("--patronymic", default="")
    create_user_parser.add_argument("--permission", dest="permissions", action="append", default=[])
    create_user_parser.add_argument("--org-slug")
    create_user_parser.add_argument("--position-title", default="")
    create_user_parser.add_argument("--photo-url")
    create_user_parser.set_defaults(func=cmd_create_user)

    news_parser = subparsers.add_parser("post-news")
    news_parser.add_argument("--actor-uin", required=True)
    news_parser.add_argument("--title", required=True)
    news_parser.add_argument("--body", required=True)
    news_parser.set_defaults(func=cmd_post_news)

    delete_news_parser = subparsers.add_parser("delete-news")
    delete_news_parser.add_argument("--actor-uin", required=True)
    delete_news_parser.add_argument("--news-id", type=int, required=True)
    delete_news_parser.set_defaults(func=cmd_delete_news)

    create_org_parser = subparsers.add_parser("create-org")
    create_org_parser.add_argument("--actor-uin", required=True)
    create_org_parser.add_argument("--name", required=True)
    create_org_parser.add_argument("--slug", required=True)
    create_org_parser.add_argument("--kind", default="government")
    create_org_parser.add_argument("--description", default="")
    create_org_parser.set_defaults(func=cmd_create_org)

    change_permissions_parser = subparsers.add_parser("change-permissions")
    change_permissions_parser.add_argument("--actor-uin", required=True)
    change_permissions_parser.add_argument("--target-uin", required=True)
    change_permissions_parser.add_argument(
        "--permission",
        dest="permissions",
        action="append",
        default=[],
    )
    change_permissions_parser.set_defaults(func=cmd_change_permissions)

    hire_parser = subparsers.add_parser("hire")
    hire_parser.add_argument("--actor-uin", required=True)
    hire_parser.add_argument("--target-uin", required=True)
    hire_parser.add_argument("--org-slug", required=True)
    hire_parser.add_argument("--position-title", required=True)
    hire_parser.set_defaults(func=cmd_hire)

    fire_parser = subparsers.add_parser("fire")
    fire_parser.add_argument("--actor-uin", required=True)
    fire_parser.add_argument("--target-uin", required=True)
    fire_parser.set_defaults(func=cmd_fire)

    bill_parser = subparsers.add_parser("create-bill")
    bill_parser.add_argument("--actor-uin", required=True)
    bill_parser.add_argument("--title", required=True)
    bill_parser.add_argument("--summary", default="")
    bill_parser.add_argument("--text", required=True)
    bill_parser.add_argument("--law-id", type=int)
    bill_parser.set_defaults(func=cmd_create_bill)

    vote_bill_parser = subparsers.add_parser("vote-bill")
    vote_bill_parser.add_argument("--actor-uin", required=True)
    vote_bill_parser.add_argument("--bill-id", type=int, required=True)
    vote_bill_parser.add_argument("--vote", choices=["yes", "no"], required=True)
    vote_bill_parser.set_defaults(func=cmd_vote_bill)

    publish_bill_parser = subparsers.add_parser("publish-bill")
    publish_bill_parser.add_argument("--actor-uin", required=True)
    publish_bill_parser.add_argument("--bill-id", type=int, required=True)
    publish_bill_parser.set_defaults(func=cmd_publish_bill)

    referendum_parser = subparsers.add_parser("create-referendum")
    referendum_parser.add_argument("--actor-uin", required=True)
    referendum_parser.add_argument("--title", required=True)
    referendum_parser.add_argument("--description", default="")
    referendum_parser.add_argument("--text", required=True)
    referendum_parser.add_argument("--law-id", type=int)
    referendum_parser.add_argument("--target-level", choices=["law", "constitution"], default="constitution")
    referendum_parser.add_argument("--closes-in-days", type=int, default=7)
    referendum_parser.set_defaults(func=cmd_create_referendum)

    vote_ref_parser = subparsers.add_parser("vote-referendum")
    vote_ref_parser.add_argument("--actor-uin", required=True)
    vote_ref_parser.add_argument("--referendum-id", type=int, required=True)
    vote_ref_parser.add_argument("--vote", choices=["yes", "no"], required=True)
    vote_ref_parser.set_defaults(func=cmd_vote_referendum)

    publish_ref_parser = subparsers.add_parser("publish-referendum")
    publish_ref_parser.add_argument("--actor-uin", required=True)
    publish_ref_parser.add_argument("--referendum-id", type=int, required=True)
    publish_ref_parser.set_defaults(func=cmd_publish_referendum)

    mail_parser = subparsers.add_parser("send-mail")
    mail_parser.add_argument("--actor-uin", required=True)
    mail_parser.add_argument("--to", required=True)
    mail_parser.add_argument("--subject", required=True)
    mail_parser.add_argument("--text", required=True)
    mail_parser.set_defaults(func=cmd_send_mail)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except PermissionError as error:
        print(f"Ошибка прав доступа: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
