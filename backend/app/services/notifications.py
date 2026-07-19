from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    CoupleMember,
    Notification,
    NotificationDeliveryAttempt,
    SubscriptionConsent,
)


class NotificationError(ValueError):
    """Raised when an in-app notification cannot be routed to the partner."""


def get_template_id(template_key: str) -> str:
    settings = get_settings()
    templates = {
        "check_in": settings.wechat_subscription_template_check_in,
        "meal_request": settings.wechat_subscription_template_meal_request,
    }
    return templates.get(template_key, "")


def queue_wechat_delivery_if_consented(
    db: Session, notification: Notification, template_key: str
) -> NotificationDeliveryAttempt | None:
    consent = db.scalar(
        select(SubscriptionConsent).where(
            SubscriptionConsent.user_id == notification.recipient_user_id,
            SubscriptionConsent.template_key == template_key,
            SubscriptionConsent.status == "accept",
        )
    )
    if consent is None or not get_template_id(template_key):
        return None

    attempt = NotificationDeliveryAttempt(
        notification_id=notification.id,
        template_key=template_key,
        status="pending",
    )
    db.add(attempt)
    return attempt


def create_partner_notification(
    db: Session,
    *,
    couple_id: str,
    actor_user_id: str,
    kind: str,
    title: str,
    body: str,
    payload: dict[str, object] | None = None,
    template_key: str | None = None,
) -> Notification:
    recipient = db.scalar(
        select(CoupleMember).where(
            CoupleMember.couple_id == couple_id,
            CoupleMember.user_id != actor_user_id,
            CoupleMember.is_active.is_(True),
        )
    )
    if recipient is None:
        raise NotificationError("No active partner is available for notification delivery")

    notification = Notification(
        couple_id=couple_id,
        recipient_user_id=recipient.user_id,
        actor_user_id=actor_user_id,
        kind=kind,
        title=title,
        body=body,
        payload=payload or {},
    )
    db.add(notification)
    db.flush()
    if template_key is not None:
        queue_wechat_delivery_if_consented(db, notification, template_key)
    return notification


def mark_delivery_result(
    attempt: NotificationDeliveryAttempt,
    *,
    status: str,
    error_code: str | None = None,
    error_message: str | None = None,
) -> None:
    attempt.status = status
    attempt.error_code = error_code
    attempt.error_message = error_message
    attempt.attempted_at = datetime.now(UTC)
