from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from src.schemas.topic import TopicCreate, TopicInDB
from src.repositories.topic_repository import TopicRepository


class TopicAlreadyExistsError(Exception):
    pass


class TopicService:

    def __init__(self, repository: TopicRepository):
        self.repository = repository

    async def create_topic(self, topic_data: TopicCreate) -> str:

        topic = TopicInDB(
            **topic_data.model_dump()
        )

        document = topic.model_dump(exclude={"id"})

        try:
            return await self.repository.create_topic(document)

        except DuplicateKeyError as exc:
            raise TopicAlreadyExistsError(
                f"Topic '{topic_data.slug}' already exists"
            ) from exc

    async def get_topic(self, slug: str) -> dict | None:
        return await self.repository.get_by_slug(slug)

    async def list_topics(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> list[dict]:

        return await self.repository.list_topics(
            skip=skip,
            limit=limit
        )