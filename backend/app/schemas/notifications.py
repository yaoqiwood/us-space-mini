from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SubscriptionStatus = Literal["accept", "reject"]


class SubscriptionConsentRequest(BaseModel):
    status: SubscriptionStatus


class SubscriptionConsentResponse(BaseModel):
    template_key: str
    status: SubscriptionStatus
    updated_at: datetime


class NotificationResponse(BaseModel):
    id: str
    kind: str
    title: str
    body: str
    payload: dict[str, object]
    read_at: datetime | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int = Field(ge=0)
