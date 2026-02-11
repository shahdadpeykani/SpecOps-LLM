"""
CodeFixer Agent.
Uses the LLM to fix code based on error logs (pylint, syntax errors).
"""
import json
from src.backend.llm_client import LLMClient

class CodeFixer:
    def __init__(self):
        self.llm_client = LLMClient()

    def fix_code(self, file_path: str, file_content: str, error_log: str) -> dict:
        """
        Attempts to fix the code given specific errors.
        Returns: {"success": bool, "fixed_content": str, "error": str}
        """
        prompt = f"""
        You are an Expert Python Developer. A file in our project has failed quality checks or has syntax errors.
        Your task is to FIX the errors while maintaining the original functionality.

        FILE PATH: {file_path}

        ERROR LOG (Pylint/Runtime Errors):
        {error_log}

        CURRENT FILE CONTENT:
        ```python
        {file_content}
        ```

        INSTRUCTIONS:
        1. Analyze the error log to understand what's wrong (e.g., typos, undefined variables, missing imports, syntax errors).
        2. Return the COMPLETE, CORRECTED file content.
        3. Do NOT shorten the file. Return the full file.
        4. Output ONLY the code, or wrap it in ```python``` blocks.
        """

        try:
            response = self.llm_client.generate_content(prompt)
            
            # Extract code from markdown if present
            fixed_content = response
            if "```python" in response:
                fixed_content = response.split("```python")[1].split("```")[0].strip()
            elif "```" in response:
                fixed_content = response.split("```")[1].split("```")[0].strip()
            
            return {
                "success": True,
                "fixed_content": fixed_content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
