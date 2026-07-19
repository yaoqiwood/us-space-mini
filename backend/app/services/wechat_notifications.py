from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Notification, NotificationDeliveryAttempt, WeChatIdentity
from app.services.notifications import get_template_id, mark_delivery_result


class WeChatNotificationError(RuntimeError):
    """Raised when WeChat cannot deliver an approved subscription message."""


class WeChatSubscriptionClient:
    token_url = "https://api.weixin.qq.com/cgi-bin/token"
    send_url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"

    def _get_access_token(self) -> str:
        settings = get_settings()
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            raise WeChatNotificationError("WeChat subscription delivery is not configured")
        try:
            response = httpx.get(
                self.token_url,
                params={
                    "grant_type": "client_credential",
                    "appid": settings.wechat_app_id,
                    "secret": settings.wechat_app_secret,
                },
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise WeChatNotificationError("Unable to obtain WeChat access token") from error
        payload = response.json()
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise WeChatNotificationError(str(payload.get("errmsg", "WeChat rejected the credentials")))
        return access_token

    def send(self, *, openid: str, template_id: str, data: dict[str, Any]) -> None:
        try:
            response = httpx.post(
                self.send_url,
                params={"access_token": self._get_access_token()},
                json={"touser": openid, "template_id": template_id, "data": data},
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise WeChatNotificationError("WeChat subscription delivery is unavailable") from error
        payload = response.json()
        if payload.get("errcode", 0) != 0:
            raise WeChatNotificationError(str(payload.get("errmsg", "WeChat rejected the message")))


def dispatch_pending_deliveries(db: Session, client: WeChatSubscriptionClient | None = None) -> int:
    client = client or WeChatSubscriptionClient()
    attempts = db.scalars(
        select(NotificationDeliveryAttempt).where(NotificationDeliveryAttempt.status == "pending")
    ).all()
    delivered = 0
    for attempt in attempts:
        notification = db.get(Notification, attempt.notification_id)
        template_id = get_template_id(attempt.template_key)
        identity = (
            db.scalar(
                select(WeChatIdentity).where(WeChatIdentity.user_id == notification.recipient_user_id)
            )
            if notification is not None
            else None
        )
        if notification is None or identity is None or not template_id:
            mark_delivery_result(attempt, status="skipped", error_message="Recipient or template unavailable")
            continue

        template_data = notification.payload.get("template_data", {})
        if not isinstance(template_data, dict):
            mark_delivery_result(attempt, status="skipped", error_message="Notification template data is invalid")
            continue
        try:
            client.send(openid=identity.openid, template_id=template_id, data=template_data)
        except WeChatNotificationError as error:
            mark_delivery_result(attempt, status="failed", error_message=str(error))
            continue
        mark_delivery_result(attempt, status="sent")
        delivered += 1
    db.commit()
    return delivered
