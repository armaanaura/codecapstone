from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection


class QuestionRepository:

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create_question(self, question: dict) -> str:

        result = await self.collection.insert_one(question)

        return str(result.inserted_id)

    async def get_by_id(self, question_id: str) -> dict | None:

        if not ObjectId.is_valid(question_id):
            return None

        return await self.collection.find_one({
            "_id": ObjectId(question_id)
        })

    async def get_by_topic(
        self,
        topic_id: str
    ) -> list[dict]:

        if not ObjectId.is_valid(topic_id):
            return []

        cursor = (
            self.collection
            .find({"topic_id": ObjectId(topic_id)})
            .sort("sequence_number", 1)
        )

        return await cursor.to_list(length=None)