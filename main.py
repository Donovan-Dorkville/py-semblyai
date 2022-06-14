import asyncio 
import aiohttp
from sys import argv
from web_requests import transcript_print

with open('api.secrects','r') as file:
    api =file.read()

async def main():
    args = argv[1:]
    tasks = []
    for i in args:
        tasks.append(
            asyncio.create_task(transcript_print(i,api))
        )

    await asyncio.gather(*tasks)

asyncio.run(main())