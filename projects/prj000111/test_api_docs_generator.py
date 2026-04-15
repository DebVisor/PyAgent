"""Tests for API documentation generator."""

import pytest
from api_docs_generator import APIDocGenerator


class TestAPIDocGenerator:
    """Test suite for APIDocGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = APIDocGenerator()
    
    def test_register_endpoint(self):
        """Test registering an endpoint."""
        def get_user(user_id: int) -> dict:
            """Get user by ID."""
            return {"id": user_id}
        
        self.generator.register_endpoint(
            get_user,
            method="GET",
            path="/users/{user_id}",
            description="Retrieve user information"
        )
        
        assert len(self.generator.endpoints) == 1
        endpoint = self.generator.endpoints[0]
        assert endpoint["path"] == "/users/{user_id}"
        assert endpoint["method"] == "GET"
        assert endpoint["name"] == "get_user"
    
    def test_extract_parameters(self):
        """Test parameter extraction."""
        def create_user(name: str, email: str, age: int = 18) -> dict:
            """Create a new user."""
            return {"name": name, "email": email, "age": age}
        
        self.generator.register_endpoint(create_user, method="POST", path="/users")
        endpoint = self.generator.endpoints[0]
        
        params = endpoint["parameters"]
        assert len(params) == 3
        assert params[0]["name"] == "name"
        assert params[0]["required"] is True
        assert params[2]["name"] == "age"
        assert params[2]["required"] is False
        assert params[2]["default"] == 18
    
    def test_generate_openapi_spec(self):
        """Test OpenAPI specification generation."""
        def list_items() -> dict:
            """List all items."""
            return {"items": []}
        
        self.generator.register_endpoint(list_items, method="GET", path="/items")
        spec = self.generator.generate_openapi_spec(title="Test API", version="2.0.0")
        
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "2.0.0"
        assert "/items" in spec["paths"]
        assert "get" in spec["paths"]["/items"]
    
    def test_generate_markdown(self):
        """Test markdown documentation generation."""
        def get_status() -> str:
            """Get system status."""
            return "OK"
        
        self.generator.register_endpoint(get_status, method="GET", path="/status")
        markdown = self.generator.generate_markdown("Status API")
        
        assert "# Status API" in markdown
        assert "GET" in markdown
        assert "/status" in markdown
        assert "get_status" in markdown
    
    def test_export_json(self):
        """Test JSON export."""
        def dummy() -> str:
            """Dummy endpoint."""
            return "test"
        
        self.generator.register_endpoint(dummy, method="GET", path="/dummy")
        spec = self.generator.generate_openapi_spec()
        json_output = self.generator.export_json(spec)
        
        assert isinstance(json_output, str)
        assert "openapi" in json_output
        assert "3.0.0" in json_output
    
    def test_multiple_endpoints(self):
        """Test registering multiple endpoints."""
        def endpoint1() -> str:
            return "test1"
        
        def endpoint2() -> str:
            return "test2"
        
        self.generator.register_endpoint(endpoint1, method="GET", path="/api/v1/endpoint1")
        self.generator.register_endpoint(endpoint2, method="POST", path="/api/v1/endpoint2")
        
        assert len(self.generator.endpoints) == 2
        spec = self.generator.generate_openapi_spec()
        assert len(spec["paths"]) == 2
