import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/16985066#16985066

import asyncio
import json
import platform

import aiohttp
import faker

from conf.config import settings


ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtdGhrdnZAZ21haWwuY29tIiwiaWF0IjoxNzAwNjIyNDA2LCJleHAiOjE3MDA2MjMzMDYsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.ICU-lXPVJT4J3-0c6fo0WwTDyfK53orR9KrPHT4e7Fs"

NUMBER_CONTACTS = 1000

fake_data = faker.Faker("uk_UA")


async def get_fake_contacts():
    for _ in range(NUMBER_CONTACTS):
        yield {
            "first_name": fake_data.first_name(),
            "last_name": fake_data.last_name(),
            "email": fake_data.email(),
            "phone": fake_data.phone_number(),
            "birthday": fake_data.date(),
            "address": fake_data.address(),
        }


async def send_data_to_api() -> None:
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    session = aiohttp.ClientSession()
    async for data in get_fake_contacts():
        try:
            await session.post(
                f"http://{settings.api_host}:{settings.api_port}/api/contacts",
                headers=headers,
                data=json.dumps(data),
            )
        except aiohttp.ClientOSError as error_message:
            print(f"Connection error: {str(error_message)}")
    await session.close()
    print("Done")


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send_data_to_api())
