from fastapi import APIRouter, HTTPException

from src.schemas.question import QuestionCreate
from src.services.question_service import QuestionService
from src.repositories.question_repository import QuestionRepository
from src.repositories.topic_repository import TopicRepository
from src.database.mongodb import database


router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/create", status_code=201)
async def create_question(question_data: QuestionCreate):

    question_repository = QuestionRepository(database["questions"])
    topic_repository = TopicRepository(database["topics"])

    service = QuestionService(
        question_repository,
        topic_repository
    )

    try:
        question_id = await service.create_question(question_data)

        return {
            "message": "Question created successfully",
            "question_id": question_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e