from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import CurrentMembership, get_current_membership
from app.db.models import Notification, SubscriptionConsent
from app.db.session import get_db
from app.schemas.notifications import (
    NotificationListResponse,
    NotificationResponse,
    SubscriptionConsentRequest,
    SubscriptionConsentResponse,
)


router = APIRouter(prefix="/notifications")


def to_notification_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        kind=notification.kind,
        title=notification.title,
        body=notification.body,
        payload=notification.payload,
        read_at=notification.read_at,
        created_at=notification.created_at,
    )


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    membership: Annotated[CurrentMembership, Depends(get_current_membership)],
    db: Annotated[Session, Depends(get_db)],
) -> NotificationListResponse:
    notifications = db.scalars(
        select(Notification)
        .where(
            Notification.couple_id == membership.couple_id,
            Notification.recipient_user_id == membership.user.id,
        )
        .order_by(Notification.created_at.desc())
    ).all()
    unread_count = db.scalar(
        select(func.count()).select_from(Notification).where(
            Notification.couple_id == membership.couple_id,
            Notification.recipient_user_id == membership.user.id,
            Notification.read_at.is_(None),
        )
    )
    return NotificationListResponse(
        items=[to_notification_response(notification) for notification in notifications],
        unread_count=unread_count or 0,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: Annotated[str, Path(min_length=36, max_length=36)],
    membership: Annotated[CurrentMembership, Depends(get_current_membership)],
    db: Annotated[Session, Depends(get_db)],
) -> NotificationResponse:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.couple_id == membership.couple_id,
            Notification.recipient_user_id == membership.user.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.read_at is None:
        notification.read_at = datetime.now(UTC)
        db.commit()
        db.refresh(notification)
    return to_notification_response(notification)


@router.put("/subscriptions/{template_key}", response_model=SubscriptionConsentResponse)
def record_subscription_consent(
    template_key: Annotated[str, Path(pattern=r"^[a-z_]{3,64}$")],
    body: SubscriptionConsentRequest,
    membership: Annotated[CurrentMembership, Depends(get_current_membership)],
    db: Annotated[Session, Depends(get_db)],
) -> SubscriptionConsentResponse:
    consent = db.scalar(
        select(SubscriptionConsent)
        .where(
            SubscriptionConsent.user_id == membership.user.id,
            SubscriptionConsent.template_key == template_key,
        )
        .with_for_update()
    )
    if consent is None:
        consent = SubscriptionConsent(
            user_id=membership.user.id,
            template_key=template_key,
            status=body.status,
        )
        db.add(consent)
    else:
        consent.status = body.status
    db.commit()
    db.refresh(consent)
    return SubscriptionConsentResponse(
        template_key=consent.template_key,
        status=consent.status,
        updated_at=consent.updated_at,
    )
