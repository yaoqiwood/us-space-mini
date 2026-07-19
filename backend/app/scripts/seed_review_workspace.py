"""Seed review-only credentials from environment variables.

This command must run against a separately configured review database, never
the production database holding the private couple's data.
"""

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import User
from app.db.session import get_session_local
from app.services.provisioning import ProvisioningError, create_private_couple


REQUIRED_ENVIRONMENT_KEYS = (
    "review_first_username",
    "review_first_display_name",
    "review_first_password",
    "review_second_username",
    "review_second_display_name",
    "review_second_password",
)


def main() -> None:
    settings = get_settings()
    if settings.environment != "review":
        raise SystemExit("Review seed command only runs when ENVIRONMENT=review")
    missing = [key for key in REQUIRED_ENVIRONMENT_KEYS if not getattr(settings, key, "")]
    if missing:
        raise SystemExit(f"Missing review seed configuration: {', '.join(missing)}")

    session = get_session_local()()
    try:
        if session.scalar(select(User.id).limit(1)) is not None:
            raise ProvisioningError("Review database already contains accounts")
        first_user = User(
            username=settings.review_first_username,
            display_name=settings.review_first_display_name,
            password_hash=hash_password(settings.review_first_password),
        )
        second_user = User(
            username=settings.review_second_username,
            display_name=settings.review_second_display_name,
            password_hash=hash_password(settings.review_second_password),
        )
        session.add_all([first_user, second_user])
        session.flush()
        create_private_couple(session, first_user, second_user)
        session.commit()
    except ProvisioningError as error:
        session.rollback()
        raise SystemExit(str(error)) from error
    finally:
        session.close()

    print("Seeded two review accounts and their private workspace.")


if __name__ == "__main__":
    main()
