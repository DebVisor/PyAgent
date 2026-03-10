import subprocess
import sys


def test_spawn_simple():
    # execute the async routine in a fresh Python subprocess to isolate runtime
    script = r"""
import asyncio
import runtime

async def inner():
    event = asyncio.Event()

    async def worker():
        event.set()

    runtime.spawn_task(worker())
    await asyncio.wait_for(event.wait(), timeout=1.0)

asyncio.run(inner())
# after event set, shut down runtime before exiting
runtime._shutdown_runtime()
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True)
    # subprocess should exit normally; crash will result in nonzero exit code
    assert result.returncode == 0, f"Spawn task script failed: {result.stderr.decode()}"
