"""
Tests for Benchmark Tool.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.tools.benchmark import run_benchmark

@patch('src.tools.benchmark.PipelineOrchestrator')
def test_benchmark_run(MockOrchestrator):
    # Mock Orchestrator Output
    mock_instance = MockOrchestrator.return_value
    mock_instance.run_pipeline.return_value = {
        "status": "Completed",
        "quality_report": {"pylint_score": 9.5, "tests_passed": 5},
        "file_count": 10
    }
    
    # Capture print output
    with patch('builtins.print') as mock_print:
        run_benchmark()
        
        # Verify calls
        assert mock_instance.run_pipeline.call_count == 3 # 3 scenarios
        
        # Verify success message printed
        calls = [str(c) for c in mock_print.mock_calls]
        assert any("Success Rate: 3/3" in c for c in calls)
