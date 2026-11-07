from fastapi import APIRouter, HTTPException

from src.schemas.topic import TopicCreate, TopicPublic
from src.services.topic_service import TopicService, TopicAlreadyExistsError
from src.repositories.topic_repository import TopicRepository
from src.database.mongodb import database

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post("/create", status_code=201)
async def create_topic(
    topic_data: TopicCreate
):  
    repository : TopicRepository = TopicRepository(database["topics"])
    service : TopicService = TopicService(repository=repository)
    try:
        topic_id = await service.create_topic(topic_data)
        return {
            "message": "Topic created successfully",
            "topic_id": topic_id
        }
    except TopicAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        ) from e


@router.get("/{slug}", response_model=TopicPublic)
async def get_topic(slug: str):
    repository = TopicRepository(database["topics"])
    service = TopicService(repository=repository)

    topic = await service.get_topic(slug)

    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic["id"] = str(topic.pop("_id"))
    return topic
