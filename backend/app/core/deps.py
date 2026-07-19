from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import TokenValidationError, decode_token
from app.db.models import Couple, CoupleMember, User
from app.db.session import get_db


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentMembership:
    user: User
    couple_id: str


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        claims = decode_token(credentials.credentials, "access")
    except TokenValidationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error

    user = db.get(User, claims.get("sub"))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    return user


def get_current_membership(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CurrentMembership:
    membership = db.scalar(
        select(CoupleMember)
        .join(Couple, Couple.id == CoupleMember.couple_id)
        .where(
            CoupleMember.user_id == user.id,
            CoupleMember.is_active.is_(True),
            Couple.is_active.is_(True),
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active couple workspace")
    return CurrentMembership(user=user, couple_id=membership.couple_id)
