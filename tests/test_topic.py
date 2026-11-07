import asyncio

from src.database.mongodb import client, database
from src.database.indexes import create_indexes

from src.schemas.topic import TopicCreate, TopicStory
from src.repositories.topic_repository import TopicRepository
from src.services.topic_service import TopicService


async def main():

    db = database
    await create_indexes(db)

    repository = TopicRepository(db["topics"])
    service = TopicService(repository)

    topic = TopicCreate(
        slug="graphs",
        title="Graph Algorithms",
        description="Learn graph algorithms through a continuous story.",

        story=TopicStory(
            title="The Lost Kingdom",
            introduction=(
                "You are an explorer tasked with rebuilding "
                "the transportation network of a lost kingdom."
            )
        )
    )

    try:
        topic_id = await service.create_topic(topic)
        print("Topic created:", topic_id)

        saved_topic = await service.get_topic("graphs")
        print("Saved topic:", saved_topic)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())