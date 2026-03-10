import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_context_components_exist(tmp_path: Path):
    from context_manager import ContextManager
    from skills_registry import SkillsRegistry

    cm = ContextManager(max_tokens=5)
    assert hasattr(cm, "push")
    registry = SkillsRegistry(tmp_path / "skills")
    skills = await registry.list_skills()
    assert isinstance(skills, list)
