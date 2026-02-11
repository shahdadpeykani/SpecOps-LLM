"""
Tests for Asset Generator.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.asset_generator import AssetGenerator

@pytest.fixture
def mock_llm():
    with patch('src.agents.asset_generator.LLMClient') as MockLLM:
        yield MockLLM

def test_generate_assets(mock_llm):
    mock_llm.return_value.generate_content.return_value = "# My Project"
    
    generator = AssetGenerator()
    srs = {"project_name": "My Project", "description": "Desc"}
    assets = generator.generate_assets(srs, ["Python"])
    
    assert "README.md" in assets
    assert ".github/workflows/python-app.yml" in assets
    assert "setup.bat" in assets
    assert "# My Project" in assets["README.md"]

@patch('src.agents.asset_generator.subprocess.run')
@patch('src.agents.asset_generator.LLMClient')
def test_initialize_git(MockLLM, mock_run):
    generator = AssetGenerator()
    success = generator.initialize_git("dummy/path")
    assert success is True
    assert mock_run.call_count == 4 # version, init, add, commit
