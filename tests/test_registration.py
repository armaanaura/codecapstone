import asyncio

from src.database.mongodb import client, database
from src.database.indexes import create_indexes
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.schemas.user import UserCreate


async def main():

    await create_indexes(database)

    repository = UserRepository(database["users"])

    service = UserService(repository)

    user = UserCreate(
        username="armaansds",
        email="armaands@example.com",
        password="SecurePassword123!"
    )

    try:
        user_id = await service.register_user(user)
        print("User created:", user_id)

    except Exception as error:
        print("Registration failed:", error)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())