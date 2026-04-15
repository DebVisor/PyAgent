"""
Tests for prj000168 - Resource Allocation Manager
"""

import pytest
from prj000168_impl import (
    ComponentStatus, ComponentConfig, ComponentResult,
    ResourceAllocationManager
)


class TestResourceAllocationManager:
    """Test suite for Resource Allocation Manager"""
    
    @pytest.fixture
    def component(self):
        return ResourceAllocationManager()
    
    @pytest.fixture
    def config(self):
        return ComponentConfig(
            name="prj000168",
            timeout=10.0,
            max_retries=2,
            metadata={"test": True}
        )
    
    def test_initialization(self, component, config):
        assert component.initialize(config)
        assert component.get_status() == ComponentStatus.IDLE
    
    def test_initialization_defaults(self, component):
        config = ComponentConfig()
        assert component.initialize(config)
    
    def test_not_initialized_execution(self, component):
        result = component.execute("test")
        assert not result.success
        assert "not initialized" in result.error.lower()
    
    def test_basic_execution(self, component, config):
        assert component.initialize(config)
        result = component.execute("test_arg")
        assert result.success
        assert result.duration_ms >= 0
        assert component.execution_count == 1
    
    def test_multiple_executions(self, component, config):
        assert component.initialize(config)
        for i in range(5):
            result = component.execute(f"arg_{i}")
            assert result.success
        assert component.execution_count == 5
    
    def test_execution_with_kwargs(self, component, config):
        assert component.initialize(config)
        result = component.execute(test_key="test_value")
        assert result.success
    
    def test_shutdown(self, component, config):
        assert component.initialize(config)
        assert component.shutdown()
        assert component.get_status() == ComponentStatus.STOPPED
    
    def test_get_metrics(self, component, config):
        assert component.initialize(config)
        component.execute("test")
        metrics = component.get_metrics()
        
        assert "execution_count" in metrics
        assert "error_count" in metrics
        assert "success_rate" in metrics
        assert metrics["execution_count"] == 1
    
    def test_handler_registration(self, component, config):
        assert component.initialize(config)
        
        called = []
        def test_handler(*args, **kwargs):
            called.append(True)
            return "handled"
        
        component.register_handler("execute", test_handler)
        result = component.execute("test")
        
        assert result.success
        assert len(called) > 0
    
    def test_multiple_handlers(self, component, config):
        assert component.initialize(config)
        
        calls = []
        for i in range(3):
            def handler(idx=i, *args, **kwargs):
                calls.append(idx)
            component.register_handler("execute", handler)
        
        result = component.execute()
        assert result.success
        assert len(calls) == 3
    
    def test_result_metadata(self, component, config):
        assert component.initialize(config)
        result = component.execute("test")
        assert isinstance(result, ComponentResult)
        assert isinstance(result.metadata, dict)
    
    def test_config_metadata(self, component):
        config = ComponentConfig(
            metadata={"version": "1.0"}
        )
        assert component.initialize(config)
        assert component.config.metadata["version"] == "1.0"


class TestComponentConfig:
    """Test ComponentConfig"""
    
    def test_default_config(self):
        config = ComponentConfig()
        assert config.name == "prj000161"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.enabled is True
    
    def test_custom_config(self):
        config = ComponentConfig(
            name="custom",
            timeout=60.0,
            max_retries=5,
            enabled=False
        )
        assert config.name == "custom"
        assert config.timeout == 60.0


class TestComponentResult:
    """Test ComponentResult"""
    
    def test_successful_result(self):
        result = ComponentResult(success=True, data={"key": "value"})
        assert result.success
        assert result.data == {"key": "value"}
        assert result.error is None
    
    def test_failed_result(self):
        result = ComponentResult(success=False, data=None, error="Test error")
        assert not result.success
        assert result.error == "Test error"
    
    def test_result_with_duration(self):
        result = ComponentResult(success=True, data=None, duration_ms=123.45)
        assert result.duration_ms == 123.45


class TestComponentIntegration:
    """Integration tests"""
    
    def test_full_lifecycle(self):
        component = ResourceAllocationManager()
        config = ComponentConfig(name="prj000168")
        
        assert component.initialize(config)
        assert component.get_status() == ComponentStatus.IDLE
        
        for i in range(3):
            result = component.execute(i)
            assert result.success
        
        metrics = component.get_metrics()
        assert metrics["execution_count"] == 3
        
        assert component.shutdown()
        assert component.get_status() == ComponentStatus.STOPPED
    
    def test_error_handling(self):
        component = ResourceAllocationManager()
        config = ComponentConfig()
        
        assert component.initialize(config)
        
        results = []
        for i in range(5):
            result = component.execute(f"input_{i}")
            results.append(result)
        
        for result in results:
            assert result.success
            assert result.error is None
