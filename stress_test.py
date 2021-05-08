import time
import asyncio

from httpx import AsyncClient

async def fetch(url, session):
    response = await session.get(url)
    delay = response.headers.get("X-Process-Time")
    date = response.headers.get("DATE")
    print("{}:{} with delay {}".format(date, response.url, delay))


async def bound_fetch(sem, url, session):
    async with sem:
        await fetch(url, session)


async def run(r):
    url = "http://localhost:80/api/v1/search/questions?q=search"
    tasks = []
    sem = asyncio.Semaphore(1000)
    async with AsyncClient(timeout=60) as session:
        for i in range(r):
            task = asyncio.ensure_future(bound_fetch(sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

number = 10000
start = time.time()
loop = asyncio.get_event_loop()

future = asyncio.ensure_future(run(number))
loop.run_until_complete(future)
print(time.time() - start)
