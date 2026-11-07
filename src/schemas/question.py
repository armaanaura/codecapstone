from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class QuestionStory(BaseModel):
    narrative: str
    objective: str


class QuestionProblem(BaseModel):
    description: str
    constraints: list[str] = Field(default_factory=list)


class SampleTestCase(BaseModel):
    input: dict
    expected_output: object
    explanation: str = ""


class EvaluationConfig(BaseModel):
    mode: Literal["exact", "custom"] = "exact"
    time_limit_ms: int = Field(default=2000, gt=0)
    memory_limit_mb: int = Field(default=256, gt=0)


class QuestionCreate(BaseModel):
    topic_slug: str

    sequence_number: int = Field(gt=0)

    title: str = Field(min_length=3, max_length=200)

    difficulty: Literal["easy", "medium", "hard"]

    story: QuestionStory

    problem: QuestionProblem

    sample_test_cases: list[SampleTestCase] = Field(
        min_length=2,
        max_length=3
    )

    evaluation: EvaluationConfig = Field(
        default_factory=EvaluationConfig
    )


class QuestionInDB(QuestionCreate):

    is_published: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )