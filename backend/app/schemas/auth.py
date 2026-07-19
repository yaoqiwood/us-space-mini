from typing import Literal

from pydantic import BaseModel, Field


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=2048)


class AccountBindRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=256)
    binding_token: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthenticatedResponse(BaseModel):
    status: Literal["authenticated"] = "authenticated"
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class BindingRequiredResponse(BaseModel):
    status: Literal["binding_required"] = "binding_required"
    binding_token: str


class CurrentUserResponse(BaseModel):
    id: str
    username: str
    display_name: str
