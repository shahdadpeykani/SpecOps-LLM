"""
Tests for CodeGenerator Agent.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.code_generator import CodeGenerator

@pytest.fixture
def mock_llm():
    with patch('src.agents.code_generator.LLMClient') as MockLLM:
        yield MockLLM

def test_code_generator_validation(mock_llm):
    """Test structure validation logic."""
    generator = CodeGenerator()
    
    # Manually inject templates for consistent testing
    generator.templates = {
        "Repository Pattern": {
            "required_structure": ["repositories"],
            "file_conventions": ["_repository.py"]
        }
    }
    
    # Case 1: Valid structure
    files_valid = {
        "src/repositories/user_repository.py": "class UserRepo...",
        "src/main.py": "print('hi')"
    }
    errors = generator._validate_structure(files_valid, ["Repository Pattern"])
    assert len(errors) == 0

    # Case 2: Missing folder
    files_missing_folder = {
        "src/user_repository.py": "class UserRepo..."
    }
    errors = generator._validate_structure(files_missing_folder, ["Repository Pattern"])
    assert any("requires folder/component 'repositories'" in e for e in errors)

    # Case 3: Missing file suffix
    files_missing_suffix = {
        "src/repositories/user_data.py": "class UserRepo..."
    }
    errors = generator._validate_structure(files_missing_suffix, ["Repository Pattern"])
    assert any("requires files ending in '_repository.py'" in e for e in errors)
