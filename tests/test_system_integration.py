import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_system_integration(tmp_path: Path) -> None:
    from context_manager import ContextManager
    from skills_registry import SkillsRegistry

    cm = ContextManager(max_tokens=5)
    registry = SkillsRegistry(tmp_path / "skills")
    # should import without error and be usable
    await cm.push("a")
    assert cm.snapshot() == "a"
    skills = await registry.list_skills()
    assert skills == []
