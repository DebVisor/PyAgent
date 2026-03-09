def test_skills_registry_scans(tmp_path):
    # create a fake skills directory
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    foo = skills_dir / "foo.yaml"
    foo.write_text("name: foo\n")

    from skills_registry import SkillsRegistry

    registry = SkillsRegistry(skills_dir)
    assert registry.list_skills() == ["foo"]
