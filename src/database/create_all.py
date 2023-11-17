import asyncio

from connect_db import engine
from models import Base


async def async_main(engine) -> None:

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(async_main(engine))
