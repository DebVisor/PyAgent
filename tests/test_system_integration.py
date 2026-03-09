def test_system_integration(tmp_path):
    from context_manager import ContextManager
    from skills_registry import SkillsRegistry

    cm = ContextManager(max_tokens=5)
    registry = SkillsRegistry(tmp_path / "skills")
    # should import without error and be usable
    cm.push("a")
    assert cm.snapshot() == "a"
    assert registry.list_skills() == []
