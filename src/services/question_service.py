from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from src.schemas.question import QuestionCreate, QuestionInDB
from src.repositories.question_repository import QuestionRepository
from src.repositories.topic_repository import TopicRepository


class QuestionService:

    def __init__(
        self,
        question_repository: QuestionRepository,
        topic_repository: TopicRepository
    ):
        self.question_repository = question_repository
        self.topic_repository = topic_repository

    async def create_question(self, question_data: QuestionCreate) -> str:

        # Find topic using its slug
        topic = await self.topic_repository.get_by_slug(
            question_data.topic_slug
        )

        if topic is None:
            raise ValueError("Topic does not exist")

        # Prepare question document
        question = QuestionInDB(**question_data.model_dump())

        document = question.model_dump(exclude={"topic_slug"})

        # Store MongoDB ObjectId internally
        document["topic_id"] = topic["_id"]

        try:
            return await self.question_repository.create_question(
                document
            )

        except DuplicateKeyError as e:
            raise ValueError(
                "Question already exists at this sequence number"
            ) from e