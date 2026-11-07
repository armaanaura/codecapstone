from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from src.schemas.user import UserCreate, UserInDB
from src.repositories.user_repository import UserRepository
from src.core.security import hash_password


class UserAlreadyExistsError(Exception):
    pass


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, user_data: UserCreate) -> str:

        # Normalize username and email
        username = user_data.username.strip().lower()
        email = str(user_data.email).strip().lower()

        # Check whether username already exists
        existing_user = await self.repository.get_by_username(username)

        if existing_user:
            raise UserAlreadyExistsError("Username already exists")

        # Check whether email already exists
        existing_user = await self.repository.get_by_email(email)

        if existing_user:
            raise UserAlreadyExistsError("Email already registered")

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create user document
        user = UserInDB(
            username=username,
            email=email,
            password_hash=hashed_password,
        )

        # Convert Pydantic model to MongoDB document
        user_document = user.model_dump(exclude={"id"})

        # we already checked for username and email, but we still need this check to avoid concurrent requests, what if user sends 2 requests and second comes after we check for email and username, that will create two users
        try:
            return await self.repository.create_user(user_document)

        except DuplicateKeyError:
            # Handles concurrent registration attempts
            raise UserAlreadyExistsError(
                "Username or email already exists"
            )