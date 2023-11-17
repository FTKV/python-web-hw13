from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from sqlalchemy import select, text
import uvicorn

from src.conf.config import settings
from src.database.connect_db import AsyncDBSession, get_session
from src.routes import auth, contacts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

origins = [f"http://{settings.api_host}:{settings.api_port}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", dependencies=[Depends(RateLimiter(times=1, seconds=1))])
async def read_root():
    return {"message": "Contacts API"}


@app.get("/api/healthchecker", dependencies=[Depends(RateLimiter(times=1, seconds=1))])
async def healthchecker(session: AsyncDBSession = Depends(get_session)):
    try:
        # Make request
        stmt = select(text("1"))
        result = await session.execute(stmt)
        result = result.scalar()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "OK"}
    except Exception as e:
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
