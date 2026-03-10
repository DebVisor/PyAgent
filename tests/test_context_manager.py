def test_context_manager_basic(tmp_path):
    from context_manager import ContextManager
    import asyncio

    async def inner():
        cm = ContextManager(max_tokens=10)
        await cm.push("hello world")
        assert cm.snapshot() == "hello world"

    asyncio.run(inner())


def test_context_manager_windowing(tmp_path):
    from context_manager import ContextManager
    import asyncio

    async def inner():
        cm = ContextManager(max_tokens=3)  # count words as tokens
        await cm.push("one")
        await cm.push("two")
        await cm.push("three")
        await cm.push("four")
        # after pushing fourth word with max_tokens=3, oldest segment should be pruned
        assert cm.snapshot() == "two" + "three" + "four"

    asyncio.run(inner())
