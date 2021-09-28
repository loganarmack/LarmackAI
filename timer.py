import asyncio


class Timer:
    def __init__(self, timeout, callback, loop=None):
        self._timeout = timeout
        self._callback = callback
        if not loop:
            self._task = asyncio.ensure_future(self._job())
        else:
            self._task = loop.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()
