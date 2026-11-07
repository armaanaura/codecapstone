from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserProfile(BaseModel):
    display_name: str = ""
    bio: str = ""
    avatar_url: str | None = None


class UserStats(BaseModel):
    total_solved: int = Field(default=0, ge=0)
    easy_solved: int = Field(default=0, ge=0)
    medium_solved: int = Field(default=0, ge=0)
    hard_solved: int = Field(default=0, ge=0)
    topics_completed: int = Field(default=0, ge=0)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)


class UserInDB(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str | None = None

    username: str
    email: EmailStr
    password_hash: str

    profile: UserProfile = Field(default_factory=UserProfile)
    stats: UserStats = Field(default_factory=UserStats)

    role: Literal["user", "admin"] = "user"
    is_active: bool = True
    email_verified: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class UserPublic(BaseModel):
    id: str
    username: str
    profile: UserProfile
    stats: UserStats
    created_at: datetime