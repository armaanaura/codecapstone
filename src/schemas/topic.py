from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TopicStory(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    introduction: str = Field(min_length=10)


class TopicCreate(BaseModel):
    slug: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )

    title: str = Field(min_length=3, max_length=100)
    description: str

    story: TopicStory


class TopicInDB(TopicCreate):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[str] = None

    total_questions: int = Field(default=0, ge=0)
    is_published: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
 
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TopicPublic(TopicCreate):
    id: str

    total_questions: int
    is_published: bool

    created_at: datetime