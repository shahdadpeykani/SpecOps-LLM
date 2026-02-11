"""
Quality Runner Module.
Responsible for running Pytest, Pylint, and Bandit.
"""
import subprocess
import os
import re

class QualityRunner:
    def __init__(self):
        pass

    def run_all_checks(self, project_path: str) -> dict:
        """
        Runs quality checks on the generated project.
        """
        print(f"Running quality checks in {project_path}")
        
        # Ensure project path is absolute and exists
        if not os.path.exists(project_path):
            return {"error": "Project path does not exist"}
        
        # Detect project type
        project_type = self._detect_project_type(project_path)
        
        # Only run Python quality checks for Python projects
        if project_type == "python":
            pylint_score = self._run_pylint(project_path)
            bandit_report = self._run_bandit(project_path)
            pytest_report = self._run_pytest(project_path)
        else:
            # For non-Python projects, return N/A
            pylint_score = f"N/A ({project_type} project)"
            bandit_report = f"N/A ({project_type} project)"
            pytest_report = f"N/A ({project_type} project)"

        return {
            "pylint_score": pylint_score,
            "bandit_issues": bandit_report,
            "tests_passed": pytest_report,
            "project_type": project_type
        }
    
    def _detect_project_type(self, path: str) -> str:
        """Detect if project is Python, HTML/JS, or other."""
        # Check for Python files
        has_python = False
        has_html = False
        
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    has_python = True
                if file.endswith('.html') or file.endswith('.js'):
                    has_html = True
        
        if has_python:
            return "python"
        elif has_html:
            return "html/js"
        else:
            return "unknown"

    def _run_pylint(self, path: str):
        try:
            # Run pylint using current python executable
            import sys
            result = subprocess.run(
                [sys.executable, "-m", "pylint", path], 
                capture_output=True, 
                text=True
            )
            output = result.stdout
            
            # Extract score using regex "Your code has been rated at X.XX/10"
            match = re.search(r"Your code has been rated at (\-?[0-9\.]+)/10", output)
            if match:
                return float(match.group(1))
            return 0.0 
        except Exception as e:
            return f"Error: {str(e)}"

    def get_pylint_report(self, path: str) -> str:
        """Runs pylint and returns the full textual output."""
        try:
            import sys
            result = subprocess.run(
                [sys.executable, "-m", "pylint", path], 
                capture_output=True, 
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error running pylint: {e}"

    def _run_bandit(self, path: str):
        try:
            import sys
            # Run bandit using current python executable
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", path, "-f", "json"], 
                capture_output=True, 
                text=True
            )
            # Bandit returns non-zero exit code if issues found
            import json
            if result.stdout.strip():
                try:
                    report = json.loads(result.stdout)
                    return {
                        "high": report.get("metrics", {}).get("_totals", {}).get("SEVERITY.HIGH", 0),
                        "medium": report.get("metrics", {}).get("_totals", {}).get("SEVERITY.MEDIUM", 0)
                    }
                except:
                    return "Could not parse bandit JSON"
            return "No output"
        except Exception as e:
            return f"Error: {str(e)}"

    def _run_pytest(self, path: str):
        try:
            import sys
            # Run pytest using current python executable
            # "-p", "no:warnings" helps clean output parsing
            result = subprocess.run(
                [sys.executable, "-m", "pytest", path], 
                capture_output=True, 
                text=True
            )
            
            # Simple interaction: check if "X passed" string exists
            output = result.stdout
            
            if "passed" in output:
                match = re.search(r"(\d+) passed", output)
                if match:
                    return int(match.group(1))
            
            if "failed" in output and "passed" not in output:
                return 0
                
            return "No tests found or failed execution"
        except Exception as e:
            return f"Error: {str(e)}"
