from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import (
    TokenValidationError,
    create_access_token,
    create_binding_token,
    create_refresh_token,
    decode_token,
    new_session_id,
    token_digest,
    verify_password,
)
from app.db.models import RefreshSession, User, WeChatIdentity
from app.db.session import get_db
from app.schemas.auth import (
    AccountBindRequest,
    AuthenticatedResponse,
    BindingRequiredResponse,
    CurrentUserResponse,
    RefreshRequest,
    WeChatLoginRequest,
)
from app.services.wechat import WeChatClient, WeChatExchangeError, get_wechat_client


router = APIRouter(prefix="/auth")


def issue_session(db: Session, user: User, openid: str) -> AuthenticatedResponse:
    session_id = new_session_id()
    refresh_token, expires_at = create_refresh_token(user.id, session_id)
    db.add(
        RefreshSession(
            id=session_id,
            user_id=user.id,
            token_hash=token_digest(refresh_token),
            expires_at=expires_at,
        )
    )
    db.flush()
    return AuthenticatedResponse(
        access_token=create_access_token(user.id),
        refresh_token=refresh_token,
        openid=openid,
    )


@router.post("/wechat", response_model=AuthenticatedResponse | BindingRequiredResponse)
def login_with_wechat(
    body: WeChatLoginRequest,
    db: Annotated[Session, Depends(get_db)],
    wechat_client: Annotated[WeChatClient, Depends(get_wechat_client)],
) -> AuthenticatedResponse | BindingRequiredResponse:
    try:
        wechat_session = wechat_client.exchange_code(body.code)
    except WeChatExchangeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    identity = db.scalar(
        select(WeChatIdentity).where(WeChatIdentity.openid == wechat_session.openid)
    )
    if identity is None:
        return BindingRequiredResponse(
            binding_token=create_binding_token(wechat_session.openid),
            openid=wechat_session.openid,
        )
    if not identity.user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")

    response = issue_session(db, identity.user, wechat_session.openid)
    db.commit()
    return response


@router.post("/bind", response_model=AuthenticatedResponse)
def bind_wechat_identity(
    body: AccountBindRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthenticatedResponse:
    try:
        claims = decode_token(body.binding_token, "bind")
        openid = claims["openid"]
    except (KeyError, TokenValidationError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Binding token is invalid") from error

    if db.scalar(select(WeChatIdentity.id).where(WeChatIdentity.openid == openid)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="WeChat account is already bound")

    user = db.scalar(
        select(User).where(User.username == body.username).with_for_update()
    )
    if user is None or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid account credentials")
    if user.wechat_identity is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account is already bound")

    db.add(WeChatIdentity(user_id=user.id, openid=openid))
    try:
        response = issue_session(db, user, openid)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="WeChat account is already bound") from error
    return response


@router.post("/refresh", response_model=AuthenticatedResponse)
def refresh_session(
    body: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthenticatedResponse:
    try:
        claims = decode_token(body.refresh_token, "refresh")
        session_id = claims["sid"]
        user_id = claims["sub"]
    except (KeyError, TokenValidationError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid") from error

    refresh_session = db.get(RefreshSession, session_id)
    now = datetime.now(UTC)
    if (
        refresh_session is None
        or refresh_session.user_id != user_id
        or refresh_session.token_hash != token_digest(body.refresh_token)
        or refresh_session.revoked_at is not None
        or refresh_session.expires_at <= now
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")

    user = db.get(User, user_id)
    if user is None or not user.is_active or user.wechat_identity is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")

    refresh_session.revoked_at = now
    response = issue_session(db, user, user.wechat_identity.openid)
    db.commit()
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    body: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    try:
        claims = decode_token(body.refresh_token, "refresh")
        session_id = claims["sid"]
    except (KeyError, TokenValidationError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid") from error

    refresh_session = db.get(RefreshSession, session_id)
    if refresh_session is None or refresh_session.token_hash != token_digest(body.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")

    if refresh_session.revoked_at is None:
        refresh_session.revoked_at = datetime.now(UTC)
        db.commit()


@router.get("/me", response_model=CurrentUserResponse)
def current_user(
    user: Annotated[User, Depends(get_current_user)],
) -> CurrentUserResponse:
    return CurrentUserResponse(id=user.id, username=user.username, display_name=user.display_name)
