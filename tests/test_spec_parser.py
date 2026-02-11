"""
Tests for SpecParser Agent.
"""
import pytest
import os
import json
from unittest.mock import MagicMock, patch
from src.agents.spec_parser import SpecParser

@pytest.fixture
def mock_llm_client():
    with patch('src.agents.spec_parser.LLMClient') as MockClient:
        yield MockClient

def test_spec_parser_init(mock_llm_client):
    """Test SpecParser initialization."""
    mock_llm_client.return_value.api_key = "fake_key"
    parser = SpecParser()
    assert parser.schema is not None

def test_spec_parser_valid_response(mock_llm_client):
    """Test parsing with a valid LLM response."""
    # Setup mock
    mock_instance = mock_llm_client.return_value
    
    valid_srs = {
        "project_name": "Test App",
        "description": "A test app",
        "tech_stack": ["Python"],
        "functional_requirements": ["Do X"],
        "non_functional_requirements": ["Fast"],
        "actors": ["User"],
        "constraints": ["None"]
    }
    
    mock_instance.generate_content.return_value = json.dumps(valid_srs)
    
    parser = SpecParser()
    result = parser.parse_input("Build a test app")
    
    assert result["success"] is True
    assert result["srs"]["project_name"] == "Test App"

def test_spec_parser_invalid_json(mock_llm_client):
    """Test parsing with invalid JSON response."""
    mock_instance = mock_llm_client.return_value
    mock_instance.generate_content.return_value = "Not JSON"
    
    parser = SpecParser()
    result = parser.parse_input("Build a bad app")
    
    assert result["success"] is False
    assert "LLM returned invalid JSON" in result["error"]
