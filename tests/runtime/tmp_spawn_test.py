import asyncio
import runtime

async def inner():
    event = asyncio.Event()

    async def worker():
        event.set()

    runtime.spawn_task(worker())
    await asyncio.wait_for(event.wait(), timeout=1.0)

asyncio.run(inner())
# shutdown tokio runtime to avoid threads touching Python after interpreter exit
import runtime as _rt
_rt._shutdown_runtime()
print('success')
