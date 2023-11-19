import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/16985066#16985066

import asyncio
import json
import platform

import aiohttp
import faker

from conf.config import settings


ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtdGhrdnZAZ21haWwuY29tIiwiaWF0IjoxNzAwMzg3MDc1LCJleHAiOjE3MDAzODc5NzUsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0._3pMtmX6mV5a6Rmt-DTEjbD18A9w2pHmBSljS36BoyQ"

NUMBER_CONTACTS = 1000


fake_data = faker.Faker("uk_UA")


async def get_fake_contacts():
    for _ in range(NUMBER_CONTACTS):
        yield (lambda x: [x[1], x[2]] if len(x) == 3 else [x[0], x[1]])(
            fake_data.name().split(" ")
        ) + [
            fake_data.email(),
            fake_data.phone_number(),
            fake_data.date(),
            fake_data.address(),
        ]


async def send_data_to_api() -> None:
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    session = aiohttp.ClientSession()
    async for first_name, last_name, email, phone, birthday, address in get_fake_contacts():
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "birthday": birthday,
            "address": address,
        }
        try:
            await session.post(
                f"http://{settings.api_host}:{settings.api_port}/api/contacts",
                headers=headers,
                data=json.dumps(data),
            )
        except aiohttp.ClientOSError as err:
            print(f"Connection error: {str(err)}")
    await session.close()
    print("Done")


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send_data_to_api())
