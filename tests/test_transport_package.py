def test_transport_package_import():
    # package should be importable once the placeholder is fixed
    import transport  # noqa: F401
    assert hasattr(transport, "__name__")
    # simple behavior check driven by TDD
    assert transport.placeholder() is True
