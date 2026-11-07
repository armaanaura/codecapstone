from pymongo import AsyncMongoClient
from src.core.config import settings

client = AsyncMongoClient(settings.MONGODB_URI)
database = client[settings.MONGODB_DB_NAME]

