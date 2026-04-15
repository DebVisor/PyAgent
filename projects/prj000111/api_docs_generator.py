"""Automated API Documentation Generator

This module provides functionality to automatically generate API documentation
from Python functions and FastAPI endpoints.
"""

from typing import Any, Dict, List, Optional, get_type_hints
import json
import inspect


class APIDocGenerator:
    """Generate API documentation from Python functions."""
    
    def __init__(self):
        self.endpoints: List[Dict[str, Any]] = []
    
    def register_endpoint(
        self,
        func,
        method: str = "GET",
        path: str = None,
        description: str = None
    ) -> None:
        """Register a function as an API endpoint."""
        if path is None:
            path = f"/{func.__name__}"
        
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        
        endpoint = {
            "path": path,
            "method": method,
            "name": func.__name__,
            "description": description or func.__doc__ or "",
            "parameters": self._extract_parameters(sig, type_hints),
            "response_schema": self._extract_return_type(type_hints)
        }
        self.endpoints.append(endpoint)
    
    def _extract_parameters(self, sig: inspect.Signature, type_hints: Dict) -> List[Dict]:
        """Extract parameters from function signature."""
        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = type_hints.get(param_name, type(None))
            param_info = {
                "name": param_name,
                "type": param_type.__name__ if hasattr(param_type, '__name__') else str(param_type),
                "required": param.default == inspect.Parameter.empty,
                "default": None if param.default == inspect.Parameter.empty else param.default
            }
            parameters.append(param_info)
        
        return parameters
    
    def _extract_return_type(self, type_hints: Dict) -> Dict:
        """Extract return type information."""
        return_type = type_hints.get('return', type(None))
        return {
            "type": return_type.__name__ if hasattr(return_type, '__name__') else str(return_type),
            "description": "Response from endpoint"
        }
    
    def generate_openapi_spec(self, title: str = "API", version: str = "1.0.0") -> Dict:
        """Generate OpenAPI specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version
            },
            "paths": {}
        }
        
        for endpoint in self.endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][method] = {
                "summary": endpoint["name"],
                "description": endpoint["description"],
                "parameters": self._openapi_parameters(endpoint["parameters"]),
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint["response_schema"]
                            }
                        }
                    }
                }
            }
        
        return spec
    
    def _openapi_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Convert parameters to OpenAPI format."""
        openapi_params = []
        for param in parameters:
            openapi_params.append({
                "name": param["name"],
                "in": "query",
                "required": param["required"],
                "schema": {
                    "type": param["type"].lower()
                }
            })
        return openapi_params
    
    def generate_markdown(self, title: str = "API Documentation") -> str:
        """Generate markdown documentation."""
        lines = [f"# {title}\n"]
        
        for endpoint in self.endpoints:
            lines.append(f"## {endpoint['name'].upper()}")
            lines.append(f"**Method:** `{endpoint['method']}`")
            lines.append(f"**Path:** `{endpoint['path']}`")
            lines.append(f"\n{endpoint['description']}\n")
            
            if endpoint['parameters']:
                lines.append("### Parameters")
                for param in endpoint['parameters']:
                    lines.append(f"- `{param['name']}` ({param['type']}): {param.get('description', '')}")
                lines.append("")
            
            lines.append("### Response")
            lines.append(f"- **Type:** {endpoint['response_schema']['type']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def export_json(self, spec: Dict) -> str:
        """Export specification as JSON string."""
        return json.dumps(spec, indent=2)
