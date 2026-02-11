"""
Sanity tests for SpecOps environment.
"""
import os
import sys

def test_imports():
    """
    Verify that core modules can be imported.
    """
    try:
        import streamlit
        import pytest
        import yaml
    except ImportError as e:
        pytest.fail(f"Dependency missing: {e}")

def test_directory_structure():
    """
    Verify that key directories exist.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    required_dirs = [
        "src/backend",
        "src/frontend",
        "src/agents",
        "src/tools",
        "data/schemas",
        "data/knowledge_base"
    ]
    for d in required_dirs:
        assert os.path.isdir(os.path.join(base_dir, d)), f"Directory missing: {d}"
