#!/usr/bin/env python3
# Copyright 2026 PyAgent Authors
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Agent memory persistence — JSON file-backed MemoryStore.

prj0000065 — agent-memory-persistence.

Each agent's memory is stored as a JSON array in:
    data/agents/<agent_id>/memory.json

Entries are appended in chronological order and returned newest-first by read().
A per-agent asyncio.Lock prevents concurrent corruption within a single process.
"""
from __future__ import annotations

import asyncio
import json
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_AGENTS_DATA_DIR = _PROJECT_ROOT / "data" / "agents"

# Only alphanumeric, hyphen, and underscore to prevent path traversal
_AGENT_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def _memory_path(agent_id: str) -> Path:
    """Return the Path to the memory file for *agent_id*.

    Raises ValueError if *agent_id* contains unsafe characters.
    """
    if not _AGENT_ID_RE.match(agent_id):
        raise ValueError(f"Invalid agent_id — only [a-zA-Z0-9_-] are allowed: {agent_id!r}")
    return _AGENTS_DATA_DIR / agent_id / "memory.json"


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------


class MemoryStore:
    """Async JSON file-backed store for per-agent conversation memory."""

    def __init__(self) -> None:
        # defaultdict returns a new Lock for each unseen agent_id
        self._locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lock_for(self, agent_id: str) -> asyncio.Lock:
        return self._locks[agent_id]

    def _read_raw(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _write_raw(self, path: Path, entries: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def append(self, agent_id: str, entry: dict) -> dict:
        """Append *entry* to the agent's memory and return the full stored entry.

        The supplied *entry* is augmented with a generated ``id`` (UUID4) and
        ``timestamp`` (ISO-8601 UTC) unless they are already present.
        """
        path = _memory_path(agent_id)
        stored = {
            "id": entry.get("id") or str(uuid.uuid4()),
            "role": entry["role"],
            "content": entry["content"],
            "session_id": entry.get("session_id"),
            "timestamp": entry.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        }
        async with self._lock_for(agent_id):
            entries = self._read_raw(path)
            entries.append(stored)
            self._write_raw(path, entries)
        return stored

    async def read(self, agent_id: str, limit: Optional[int] = None) -> list[dict]:
        """Return stored entries for *agent_id*, newest-first.

        If *limit* is given, only the most recent *limit* entries are returned.
        """
        path = _memory_path(agent_id)
        async with self._lock_for(agent_id):
            entries = self._read_raw(path)
        # newest-first
        result = list(reversed(entries))
        if limit is not None:
            result = result[:limit]
        return result

    async def clear(self, agent_id: str) -> None:
        """Delete all stored entries for *agent_id*."""
        path = _memory_path(agent_id)
        async with self._lock_for(agent_id):
            self._write_raw(path, [])


# Module-level singleton
memory_store = MemoryStore()
