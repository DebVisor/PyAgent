# runtime module should be importable once built; no separate test needed
# earlier iterations verified ImportError before installation.

def test_runtime_stubs_present():
    import runtime
    assert hasattr(runtime, "spawn_task")
    assert hasattr(runtime, "set_timeout")
    assert hasattr(runtime, "create_queue")
