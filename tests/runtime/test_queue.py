import asyncio
import runtime_py as runtime


def test_queue_basic() -> None:
    """Create a queue, send a message, and receive it from the same event loop."""

    async def inner() -> None:
        q, put = runtime.create_queue()
        # the put object should be awaitable
        await put("hello")
        val = await q.get()
        assert val == "hello"

    asyncio.run(inner())
