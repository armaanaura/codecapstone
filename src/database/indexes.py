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
    
    topics = db["topics"]

    await topics.create_index(
        [("slug", 1)],
        unique=True
    )

    await topics.create_index(
        [("created_at", -1)]
    )
    
    questions = db["questions"]

    await questions.create_index(
        [
            ("topic_id", 1),
            ("sequence_number", 1)
        ],
        unique=True
    )