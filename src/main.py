from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.topics import router as topics_router
from src.api.v1.questions import router as questions_router
from src.database.mongodb import client, database
from src.database.indexes import create_indexes


@asynccontextmanager #It converts an asynchronous generator function containing yield into an asynchronous context manager.
async def lifespan(app: FastAPI):
    # Runs when FastAPI starts
    await client.admin.command("ping")
    print("MongoDB connected successfully")

    await create_indexes(database)
    print("Database Indexes updates successfully")

    yield #everything before yield executes before during startup and everything after it, will be executed during shutdown

    # Runs when FastAPI shuts down
    await client.close()


app = FastAPI(
    title="CodeCapstone",
    version="1.0.0",
    lifespan=lifespan
)

# Register topic endpoints
app.include_router(topics_router, prefix="/api/v1")
app.include_router(questions_router, prefix="/api/v1")


@app.get("/")
async def home():
    return {"message": "Welcome to CodeCapstone"}