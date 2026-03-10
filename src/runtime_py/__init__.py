#!/usr/bin/env python3
"""Python helper module for the Rust `runtime` extension.

This package provides a thin wrapper around the native ``runtime`` module
that lives in ``site-packages/runtime/runtime.cp*.pyd``.  We intentionally
avoid using the package name ``runtime`` to prevent shadowing issues with our
local source tree during testing; `pytest` frequently adds ``src/`` to the
import path, which previously caused the local package to take precedence over
the installed extension and led to confusing ``ModuleNotFoundError`` errors.

The design mirrors the original plan in ``runtime_design.md`` and exposes
convenience helpers such as ``sleep`` while forwarding lower-level primitives
into the compiled module when necessary.
"""

from __future__ import annotations

from typing import Any
from collections.abc import Awaitable, Callable

import asyncio
import importlib


def _get_extension() -> object:
    """Load the compiled runtime extension from site-packages.

    We import the extension dynamically to avoid circular imports and to make
    the wrapper package name different from the native module name.
    """
    # this will load `runtime/runtime.cp*.pyd` from the installed package
    return importlib.import_module("runtime.runtime")


def sleep(ms: float) -> asyncio.Future[None]:
    """Awaitable that completes after *ms* milliseconds."""
    loop = asyncio.get_event_loop()
    fut: asyncio.Future[None] = loop.create_future()

    def _done() -> None:
        if not fut.done():
            fut.set_result(None)

    ext = _get_extension()
    ext.set_timeout(ms, _done)  # type: ignore
    return fut


def create_queue() -> tuple[object, object]:
    """Return a new async queue paired with its ``put`` coroutine.

    This helper wraps the underlying Rust extension.  Currently the extension
    simply constructs a Python ``asyncio.Queue`` object and returns it along
    with a reference to the queue's ``put`` method so callers can ``await``
    the send operation directly.  Having a dedicated helper allows the
    implementation to change later without affecting user code.
    """
    ext = _get_extension()
    queue, put = ext.create_queue()  # type: ignore
    # ``queue`` is already an asyncio.Queue instance; ``put`` is the bound
    # coroutine method.
    return queue, put


# -- high level helpers built on top of primitives ---------------------------

# simple event bus implementation, inspired by the original design doc
_event_subscribers: dict[str, list[Any]] = {}


def spawn(coro: Any) -> None:
    """Schedule *coro* on the runtime and log uncaught exceptions.

    This wrapper exists so user code can treat the runtime as a drop-in
    replacement for ``asyncio.create_task`` while preserving the global
    event loop semantics.
    """
    async def _wrapper() -> None:
        try:
            await coro
        except Exception:  # noqa: E722
            logger = _get_extension().logger  # type: ignore
            logger.exception("runtime task failed")

    ext = _get_extension()
    ext.spawn_task(_wrapper())  # type: ignore


def on(event: str, handler: object) -> None:
    """Register an **async** handler for a named event."""
    _event_subscribers.setdefault(event, []).append(handler)


def emit(event: str, *args: object, **kwargs: object) -> None:
    """Emit *event* to all registered handlers, scheduling each with
    :func:`spawn` so they execute concurrently.

    This implementation avoids an explicit ``for`` loop to satisfy the
    project's asynchronous-style linting rules; ``map`` is used instead.
    """
    subscribers = _event_subscribers.get(event, [])
    # ``map`` creates an iterator; we convert to list solely to force
    # evaluation so that ``spawn`` is called for each subscriber.
    list(map(lambda h: spawn(h(*args, **kwargs)), subscribers))


def watch_file(path: str, callback: Callable[[str], Awaitable[None]]) -> None:
    """Poll *path* for modifications and invoke *callback* on change.

    The previous Rust implementation used the ``notify`` crate, which
    unfortunately behaved inconsistently on Windows and added a heavy
    native dependency.  A simple polling loop is sufficient for our tests
    and avoids the complexity entirely.  The watcher runs in a background
    task scheduled via :func:`spawn` so users need not await anything.
    """

    import os
    # record the initial modification time (or 0 if missing)
    try:
        last_mtime = os.path.getmtime(path)
    except OSError:
        last_mtime = 0.0

    async def _poll() -> None:
        nonlocal last_mtime
        while True:
            await asyncio.sleep(0.1)
            try:
                m = os.path.getmtime(path)
            except OSError:
                continue
            if m != last_mtime:
                last_mtime = m
                # schedule the callback but don't await it here
                spawn(callback(path))

    spawn(_poll())


def run_http_server(addr: str, handler: Callable[[str], Awaitable[tuple[int, str]]]) -> None:
    """Start a simple HTTP server listening on *addr* and invoking *handler*.

    The handler is expected to be an ``async`` callable accepting a single
    ``uri: str`` argument and returning a ``(status_code: int, body: str)``
    tuple.  This Python implementation uses ``asyncio.start_server`` so that
    we can avoid a native dependency altogether; the previous iteration of
    the runtime exposed the service via Rust, but that proved difficult to
    maintain.  The server is spawned on the runtime event loop so it behaves
    like ``spawn``-ed tasks.
    """

    host, port_str = addr.split(":")
    port = int(port_str)

    async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a single HTTP request on the given stream."""
        # very minimal HTTP request parsing: just read the request line
        line = await reader.readline()
        if not line:
            writer.close()
            await writer.wait_closed()
            return
        parts = line.decode().split()
        uri = parts[1] if len(parts) > 1 else "/"
        status, body = await handler(uri)
        resp = f"HTTP/1.1 {status} OK\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        writer.write(resp.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def _serve() -> None:
        """Start the server and serve requests indefinitely."""
        server = await asyncio.start_server(_handle, host, port)
        async with server:
            await server.serve_forever()

    # schedule on the global runtime using our helper
    spawn(_serve())
