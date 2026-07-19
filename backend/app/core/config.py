from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables, never from source control."""

    environment: str = "development"
    database_url: str = "mysql+pymysql://couple_space:couple_space_dev_only@127.0.0.1:3306/couple_space"
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=30, ge=5, le=120)
    refresh_token_days: int = Field(default=30, ge=1, le=90)
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_code2session_url: str = "https://api.weixin.qq.com/sns/jscode2session"
    wechat_subscription_template_check_in: str = ""
    wechat_subscription_template_meal_request: str = ""
    review_first_username: str = ""
    review_first_display_name: str = ""
    review_first_password: str = ""
    review_second_username: str = ""
    review_second_display_name: str = ""
    review_second_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
