import asyncio
from parseTime import parseTime

async def delay(duration):
	timeToSleep = parseTime(duration)
    await asyncio.sleep(timeToSleep)