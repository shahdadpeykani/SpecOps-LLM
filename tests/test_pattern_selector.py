"""
Tests for PatternSelector Agent.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.agents.pattern_selector import PatternSelector

@pytest.fixture
def mock_dependencies():
    with patch('src.agents.pattern_selector.RAGEngine') as MockRAG, \
         patch('src.agents.pattern_selector.LLMClient') as MockLLM:
        yield MockRAG, MockLLM

def test_pattern_selector(mock_dependencies):
    """Test pattern selection flow."""
    MockRAG, MockLLM = mock_dependencies
    
    # Mock RAG retrieve
    mock_rag_instance = MockRAG.return_value
    mock_rag_instance.retrieve.return_value = [
        {"pattern": {"name": "MVC", "description": "Model View Controller"}, "score": 0.9}
    ]
    
    # Mock LLM response
    mock_llm_instance = MockLLM.return_value
    mock_llm_instance.generate_content.return_value = '{"selected_patterns": ["MVC"], "justification": "Because it is a web app"}'
    
    selector = PatternSelector()
    srs = {
        "project_name": "Web App",
        "description": "A simple web app",
        "tech_stack": ["Python"]
    }
    
    result = selector.select_patterns(srs)
    
    assert result["success"] is True
    assert "MVC" in result["selected_patterns"]
    assert result["candidates_considered"] == ["MVC"]
