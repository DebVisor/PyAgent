def test_generate_milestones(tmp_path):
    from roadmap import milestones

    import asyncio
    out = tmp_path / "roadmap.md"
    asyncio.run(milestones.create(out, ["Q1: start", "Q2: scale"]))
    text = out.read_text()
    assert "Q1" in text and "Q2" in text
