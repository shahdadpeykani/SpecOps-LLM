"""
Tests for Explainer Module.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.explainability.explainer import Explainer

@pytest.fixture
def mock_llm():
    with patch('src.explainability.explainer.LLMClient') as MockLLM:
        yield MockLLM

def test_explainer_generation(mock_llm):
    """Test standard explanation generation."""
    mock_llm.return_value.generate_content.return_value = "This design is good because..."
    
    explainer = Explainer()
    srs = {"project_name": "Test"}
    patterns = ["MVC"]
    quality = {"score": 10}
    
    result = explainer.generate_explanation(srs, patterns, quality)
    
    assert "This design is good" in result
    mock_llm.return_value.generate_content.assert_called_once()
