import tempfile


def test_parse_manifest(tmp_path):
    from importer import config
    import asyncio

    async def inner():
        manifest = tmp_path / "github.md"
        manifest.write_text("foo/bar\n")

        repos = await config.parse_manifest(manifest)
        assert repos == [("foo", "bar")]

    asyncio.run(inner())
