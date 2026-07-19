import argparse
from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models import User
from app.db.session import get_session_local
from app.services.provisioning import ProvisioningError, create_private_couple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Provision the two private Couple Space accounts.")
    parser.add_argument("--first-username", required=True)
    parser.add_argument("--first-display-name", required=True)
    parser.add_argument("--second-username", required=True)
    parser.add_argument("--second-display-name", required=True)
    return parser.parse_args()


def prompt_password(label: str) -> str:
    password = getpass(f"Password for {label}: ")
    confirmation = getpass(f"Confirm password for {label}: ")
    if password != confirmation:
        raise ProvisioningError(f"Passwords for {label} do not match")
    if len(password) < 12:
        raise ProvisioningError("Passwords must contain at least 12 characters")
    return password


def main() -> None:
    args = parse_args()
    if args.first_username == args.second_username:
        raise SystemExit("The two usernames must be different")

    first_password = prompt_password(args.first_username)
    second_password = prompt_password(args.second_username)
    session = get_session_local()()
    try:
        existing = session.scalar(select(User.id).limit(1))
        if existing is not None:
            raise ProvisioningError("The database already contains accounts; refusing to overwrite them")

        first_user = User(
            username=args.first_username,
            display_name=args.first_display_name,
            password_hash=hash_password(first_password),
        )
        second_user = User(
            username=args.second_username,
            display_name=args.second_display_name,
            password_hash=hash_password(second_password),
        )
        session.add_all([first_user, second_user])
        session.flush()
        couple = create_private_couple(session, first_user, second_user)
        session.commit()
    except ProvisioningError as error:
        session.rollback()
        raise SystemExit(str(error)) from error
    finally:
        session.close()

    print(f"Provisioned private workspace {couple.id} for {args.first_username} and {args.second_username}.")


if __name__ == "__main__":
    main()
