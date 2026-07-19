import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import CoupleMember, User
from app.services.provisioning import ProvisioningError, create_private_couple


def create_user(db_session: Session, username: str) -> User:
    user = User(
        username=username,
        display_name=username.title(),
        password_hash=hash_password("correct-password"),
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_private_workspace_has_exactly_two_provisioned_members(db_session: Session) -> None:
    alice = create_user(db_session, "alice")
    bob = create_user(db_session, "bob")

    couple = create_private_couple(db_session, alice, bob)
    db_session.commit()

    members = db_session.scalars(
        select(CoupleMember).where(CoupleMember.couple_id == couple.id)
    ).all()
    assert {member.user_id for member in members} == {alice.id, bob.id}


def test_second_active_workspace_is_rejected(db_session: Session) -> None:
    alice = create_user(db_session, "alice")
    bob = create_user(db_session, "bob")
    charlie = create_user(db_session, "charlie")
    create_private_couple(db_session, alice, bob)
    db_session.commit()

    with pytest.raises(ProvisioningError, match="already exists"):
        create_private_couple(db_session, charlie, bob)
