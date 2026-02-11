"""
Tests for QualityRunner.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.tools.quality_runner import QualityRunner

@pytest.fixture
def runner():
    return QualityRunner()

@patch('src.tools.quality_runner.subprocess.run')
def test_pylint(mock_run, runner):
    # Mock output
    mock_run.return_value.stdout = "Your code has been rated at 8.50/10"
    score = runner._run_pylint("dummy/path")
    assert score == 8.50

@patch('src.tools.quality_runner.subprocess.run')
def test_pytest_parse(mock_run, runner):
    # Mock output
    mock_run.return_value.stdout = "=== 5 passed, 1 failed in 0.1s ==="
    passed_count = runner._run_pytest("dummy/path")
    assert passed_count == 5

@patch('src.tools.quality_runner.subprocess.run')
def test_bandit_parse(mock_run, runner):
    # Mock output
    mock_run.return_value.stdout = '{"metrics": {"_totals": {"SEVERITY.HIGH": 0, "SEVERITY.MEDIUM": 2}}}'
    report = runner._run_bandit("dummy/path")
    assert report["high"] == 0
    assert report["medium"] == 2
