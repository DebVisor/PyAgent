def test_compile_architecture(tmp_path):
    from importer import compile
    import asyncio

    async def inner():
        descs = [{"path": "a/b"}, {"path": "c/d"}]
        out = tmp_path / "architecture.md"
        await compile.compile_architecture(descs, out)
        assert out.exists()
        text = out.read_text()
        assert "a/b" in text and "c/d" in text

    asyncio.run(inner())
