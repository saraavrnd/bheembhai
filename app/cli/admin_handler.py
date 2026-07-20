from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from app.auth.repository import ADMIN_ROLE, STANDARD_ROLE
from app.auth.service import build_auth_service
from app.core.settings import get_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beembhai-admin", description="BheemBhai admin handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-admin",
        help="Create the first platform admin or leave the existing one untouched",
    )
    bootstrap_parser.add_argument("--email", required=True, help="Platform admin email address")
    bootstrap_parser.add_argument("--password", required=True, help="Platform admin password")
    bootstrap_parser.add_argument(
        "--verified",
        action="store_true",
        help=(
            "Mark the created admin's email as already verified and skip sending the "
            "verification email (for automated/non-interactive bootstrapping, e.g. test "
            "and CI environments)"
        ),
    )

    upsert_parser = subparsers.add_parser(
        "upsert-user",
        help="Create or update a local user record",
    )
    upsert_parser.add_argument("--email", required=True, help="User email address")
    upsert_parser.add_argument("--password", required=True, help="User password")
    upsert_parser.add_argument(
        "--role",
        choices=[ADMIN_ROLE, STANDARD_ROLE],
        default=STANDARD_ROLE,
        help="Platform role to apply",
    )

    deactivate_parser = subparsers.add_parser(
        "deactivate-user",
        help="Deactivate a user so they can no longer authenticate",
    )
    deactivate_parser.add_argument("--email", required=True, help="User email address")

    activate_parser = subparsers.add_parser(
        "activate-user",
        help="Re-activate a previously deactivated user",
    )
    activate_parser.add_argument("--email", required=True, help="User email address")
    return parser


def _print_user_action(command: str, action: str, user: object) -> None:
    print(
        json.dumps(
            {
                "command": command,
                "action": action,
                "skipped_reason": None,
                "verification_email_sent": False,
                "user": asdict(user),
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()
    service = build_auth_service(settings)

    if args.command == "bootstrap-admin":
        result = service.bootstrap_platform_admin(
            email=args.email, password=args.password, verified=args.verified
        )
    elif args.command == "upsert-user":
        result = service.upsert_user(
            email=args.email,
            password=args.password,
            platform_role=args.role,
        )
    elif args.command == "deactivate-user":
        user = service.deactivate_user(email=args.email)
        _print_user_action(args.command, "deactivated", user)
        return 0
    elif args.command == "activate-user":
        user = service.activate_user(email=args.email)
        _print_user_action(args.command, "activated", user)
        return 0
    else:  # pragma: no cover - argparse guarantees this branch is unreachable.
        parser.error(f"unsupported command: {args.command}")

    user_payload = asdict(result.user)
    print(
        json.dumps(
            {
                "command": args.command,
                "action": result.action,
                "skipped_reason": result.skipped_reason,
                "verification_email_sent": result.verification_email_sent,
                "user": user_payload,
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
