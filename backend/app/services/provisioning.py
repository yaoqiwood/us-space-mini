from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Couple, CoupleMember, User


class ProvisioningError(ValueError):
    """Raised when private-workspace provisioning would break its invariants."""


def create_private_couple(db: Session, first_user: User, second_user: User) -> Couple:
    """Create the one active workspace and its two approved members.

    This service is deliberately not exposed through a public API. An operator
    uses it only while provisioning the two accounts for this private product.
    """

    if first_user.id == second_user.id:
        raise ProvisioningError("A couple requires two different accounts")
    if not first_user.is_active or not second_user.is_active:
        raise ProvisioningError("Only active accounts can join the workspace")
    if db.scalar(select(Couple.id).where(Couple.is_active.is_(True))) is not None:
        raise ProvisioningError("An active couple workspace already exists")

    member_count = db.scalar(
        select(func.count()).select_from(CoupleMember).where(
            CoupleMember.user_id.in_([first_user.id, second_user.id])
        )
    )
    if member_count:
        raise ProvisioningError("An account already belongs to a workspace")

    couple = Couple(is_active=True)
    db.add(couple)
    db.flush()
    db.add_all(
        [
            CoupleMember(couple_id=couple.id, user_id=first_user.id, is_active=True),
            CoupleMember(couple_id=couple.id, user_id=second_user.id, is_active=True),
        ]
    )
    db.flush()
    return couple
