import asyncio
import pytest

from runtime_py import on, emit


@pytest.mark.asyncio
async def test_event_bus():
    events: list[tuple[str, int]] = []

    async def handler1(x: int) -> None:
        events.append(("h1", x))

    async def handler2(x: int) -> None:
        events.append(("h2", x))

    on("foo", handler1)
    on("foo", handler2)

    emit("foo", 42)
    # allow the spawned tasks to run
    await asyncio.sleep(0.01)

    assert ("h1", 42) in events
    assert ("h2", 42) in events
