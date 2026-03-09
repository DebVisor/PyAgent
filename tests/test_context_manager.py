def test_context_manager_basic(tmp_path):
    from context_manager import ContextManager

    cm = ContextManager(max_tokens=10)
    cm.push("hello world")
    assert cm.snapshot() == "hello world"


def test_context_manager_windowing(tmp_path):
    from context_manager import ContextManager

    cm = ContextManager(max_tokens=3)  # count words as tokens
    cm.push("one")
    cm.push("two")
    cm.push("three")
    cm.push("four")
    # after pushing fourth word with max_tokens=3, oldest segment should be pruned
    assert cm.snapshot() == "two" + "three" + "four"
