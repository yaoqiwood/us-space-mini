from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import get_wechat_client
from app.core.security import hash_password
from app.db.models import User, WeChatIdentity
from app.main import app
from app.services.wechat import WeChatSession


class FakeWeChatClient:
    def exchange_code(self, code: str) -> WeChatSession:
        return WeChatSession(openid=f"openid-{code}")


def add_user(db_session: Session, username: str = "alice") -> User:
    user = User(
        username=username,
        display_name="Alice",
        password_hash=hash_password("correct-password"),
    )
    db_session.add(user)
    db_session.commit()
    return user


def set_wechat_override() -> None:
    app.dependency_overrides[get_wechat_client] = FakeWeChatClient


def test_unbound_wechat_login_requires_account_binding(client: TestClient) -> None:
    set_wechat_override()

    response = client.post("/v1/auth/wechat", json={"code": "new-device"})

    assert response.status_code == 200
    assert response.json()["status"] == "binding_required"
    assert "binding_token" in response.json()
    assert "openid" not in response.json()


def test_first_bind_then_wechat_login_issues_session(client: TestClient, db_session: Session) -> None:
    add_user(db_session)
    set_wechat_override()

    first_login = client.post("/v1/auth/wechat", json={"code": "alice-phone"})
    bind = client.post(
        "/v1/auth/bind",
        json={
            "username": "alice",
            "password": "correct-password",
            "binding_token": first_login.json()["binding_token"],
        },
    )

    assert bind.status_code == 200
    assert bind.json()["status"] == "authenticated"
    assert bind.json()["token_type"] == "bearer"
    assert db_session.scalar(select(WeChatIdentity).where(WeChatIdentity.openid == "openid-alice-phone"))

    second_login = client.post("/v1/auth/wechat", json={"code": "alice-phone"})

    assert second_login.status_code == 200
    assert second_login.json()["status"] == "authenticated"


def test_existing_binding_cannot_be_taken_by_another_account(
    client: TestClient, db_session: Session
) -> None:
    alice = add_user(db_session, "alice")
    add_user(db_session, "bob")
    db_session.add(WeChatIdentity(user_id=alice.id, openid="openid-alice-phone"))
    db_session.commit()
    set_wechat_override()

    login = client.post("/v1/auth/wechat", json={"code": "bob-phone"})
    response = client.post(
        "/v1/auth/bind",
        json={
            "username": "alice",
            "password": "correct-password",
            "binding_token": login.json()["binding_token"],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Account is already bound"


def test_private_api_rejects_missing_access_token(client: TestClient) -> None:
    response = client.get("/v1/auth/me")

    assert response.status_code == 401


def test_refresh_token_can_be_revoked_by_logout(client: TestClient, db_session: Session) -> None:
    add_user(db_session)
    set_wechat_override()

    first_login = client.post("/v1/auth/wechat", json={"code": "alice-phone"})
    bind = client.post(
        "/v1/auth/bind",
        json={
            "username": "alice",
            "password": "correct-password",
            "binding_token": first_login.json()["binding_token"],
        },
    )
    refresh_token = bind.json()["refresh_token"]

    logout = client.post("/v1/auth/logout", json={"refresh_token": refresh_token})
    refresh = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert logout.status_code == 204
    assert refresh.status_code == 401
