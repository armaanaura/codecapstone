from pymongo.asynchronous.database import AsyncDatabase


async def create_indexes(db: AsyncDatabase):

    users = db["users"]

    await users.create_index(
        [("username", 1)],
        unique=True
    )

    await users.create_index(
        [("email", 1)],
        unique=True
    )