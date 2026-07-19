from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.models import Notification, NotificationDeliveryAttempt, SubscriptionConsent, User, WeChatIdentity
from app.services.notifications import create_partner_notification
from app.services.provisioning import create_private_couple
from app.services.wechat_notifications import (
    WeChatNotificationError,
    WeChatSubscriptionClient,
    dispatch_pending_deliveries,
)


def create_member(db_session: Session, username: str) -> User:
    user = User(
        username=username,
        display_name=username.title(),
        password_hash=hash_password("correct-password"),
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_workspace(db_session: Session) -> tuple[User, User, str]:
    alice = create_member(db_session, "alice")
    bob = create_member(db_session, "bob")
    couple = create_private_couple(db_session, alice, bob)
    db_session.commit()
    return alice, bob, couple.id


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def test_recipient_can_list_and_read_only_their_notifications(
    client: TestClient, db_session: Session
) -> None:
    alice, bob, couple_id = create_workspace(db_session)
    notification = create_partner_notification(
        db_session,
        couple_id=couple_id,
        actor_user_id=alice.id,
        kind="check_in",
        title="报备",
        body="已到家",
    )
    db_session.commit()

    listed = client.get("/v1/notifications", headers=auth_headers(bob))
    blocked = client.post(f"/v1/notifications/{notification.id}/read", headers=auth_headers(alice))
    marked_read = client.post(f"/v1/notifications/{notification.id}/read", headers=auth_headers(bob))

    assert listed.status_code == 200
    assert listed.json()["unread_count"] == 1
    assert listed.json()["items"][0]["id"] == notification.id
    assert blocked.status_code == 404
    assert marked_read.status_code == 200
    assert marked_read.json()["read_at"] is not None


def test_subscription_consent_is_recorded_for_current_member(
    client: TestClient, db_session: Session
) -> None:
    _, bob, _ = create_workspace(db_session)

    response = client.put(
        "/v1/notifications/subscriptions/check_in",
        json={"status": "accept"},
        headers=auth_headers(bob),
    )

    assert response.status_code == 200
    assert response.json()["template_key"] == "check_in"
    assert response.json()["status"] == "accept"


def test_partner_notification_keeps_in_app_delivery_when_no_consent(db_session: Session) -> None:
    alice, bob, couple_id = create_workspace(db_session)

    notification = create_partner_notification(
        db_session,
        couple_id=couple_id,
        actor_user_id=alice.id,
        kind="meal_request",
        title="点餐",
        body="请做番茄鸡蛋面",
        template_key="meal_request",
    )
    db_session.commit()

    assert notification.recipient_user_id == bob.id
    assert db_session.scalar(select(Notification).where(Notification.id == notification.id)) is not None
    assert db_session.scalar(select(NotificationDeliveryAttempt)) is None


def test_failed_wechat_delivery_keeps_the_in_app_notification(
    db_session: Session, monkeypatch
) -> None:
    alice, bob, couple_id = create_workspace(db_session)
    db_session.add(WeChatIdentity(user_id=bob.id, openid="bob-openid"))
    db_session.add(SubscriptionConsent(user_id=bob.id, template_key="check_in", status="accept"))
    monkeypatch.setattr(get_settings(), "wechat_subscription_template_check_in", "template-id")
    notification = create_partner_notification(
        db_session,
        couple_id=couple_id,
        actor_user_id=alice.id,
        kind="check_in",
        title="报备",
        body="已到家",
        payload={"template_data": {}},
        template_key="check_in",
    )
    db_session.commit()

    class FailingClient(WeChatSubscriptionClient):
        def send(self, *, openid: str, template_id: str, data: dict[str, object]) -> None:
            raise WeChatNotificationError("simulated WeChat failure")

    assert dispatch_pending_deliveries(db_session, FailingClient()) == 0
    attempt = db_session.scalar(select(NotificationDeliveryAttempt))

    assert attempt is not None
    assert attempt.status == "failed"
    assert db_session.get(Notification, notification.id) is not None
