from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection


class UserRepository:

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create_user(self, user: dict) -> str:
        result = await self.collection.insert_one(user)
        return str(result.inserted_id)

    async def get_by_id(self, user_id: str) -> dict | None:
        if not ObjectId.is_valid(user_id):
            return None

        return await self.collection.find_one({
            "_id": ObjectId(user_id)
        })

    async def get_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({
            "email": email
        })

    async def get_by_username(self, username: str) -> dict | None:
        return await self.collection.find_one({
            "username": username
        })

    async def update_user(self, user_id: str, updates: dict) -> bool:
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )

        return result.matched_count > 0
