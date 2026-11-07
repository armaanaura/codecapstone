from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection


class TopicRepository:

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create_topic(self, topic: dict) -> str:
        result = await self.collection.insert_one(topic)
        return str(result.inserted_id)

    async def get_by_id(self, topic_id: str) -> dict | None:

        if not ObjectId.is_valid(topic_id):
            return None

        return await self.collection.find_one({
            "_id": ObjectId(topic_id)
        })

    async def get_by_slug(self, slug: str) -> dict | None:
        return await self.collection.find_one({
            "slug": slug
        })

    async def list_topics(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> list[dict]:

        cursor = (
            self.collection
            .find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def update_topic(
        self,
        topic_id: str,
        updates: dict
    ) -> bool:

        if not ObjectId.is_valid(topic_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(topic_id)},
            {"$set": updates}
        )

        return result.matched_count > 0