from dataclasses import dataclass

import httpx

from app.core.config import get_settings


class WeChatExchangeError(RuntimeError):
    """Raised when WeChat cannot exchange a Mini Program login code."""


@dataclass(frozen=True)
class WeChatSession:
    openid: str


class WeChatClient:
    def exchange_code(self, code: str) -> WeChatSession:
        settings = get_settings()
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            raise WeChatExchangeError("WeChat login is not configured")

        try:
            response = httpx.get(
                settings.wechat_code2session_url,
                params={
                    "appid": settings.wechat_app_id,
                    "secret": settings.wechat_app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise WeChatExchangeError("WeChat login is unavailable") from error

        payload = response.json()
        openid = payload.get("openid")
        if not isinstance(openid, str) or not openid:
            raise WeChatExchangeError("WeChat rejected the login code")
        return WeChatSession(openid=openid)


def get_wechat_client() -> WeChatClient:
    return WeChatClient()
