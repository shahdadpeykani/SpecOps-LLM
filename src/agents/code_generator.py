"""
CodeGenerator Agent.
Generates full project structure and code based on SRS, Patterns, and Templates.
"""
import json
import os
import yaml
from src.backend.llm_client import LLMClient

class CodeGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
    def __init__(self):
        self.llm_client = LLMClient()
        self.templates = {}
        # Templates removed as we switched to Vector DB and LLM knowledge


    def generate_code(self, srs: dict, selected_patterns: list) -> dict:
        """
        Generates code structure. Returns a dict: { "filename": "content" }
        """
        # 1. Get Structural Rules from Templates
        rules = []
        for pattern in selected_patterns:
            if pattern in self.templates:
                rules.append(f"Pattern '{pattern}' Requirements: \n {json.dumps(self.templates[pattern], indent=2)}")
        
        rules_str = "\n".join(rules) if rules else "No specific structural rules."

        # 2. Construct Prompt
        prompt = f"""
        You are an Expert Software Developer. Generate a complete, runnable codebase for the following project.
        
        SRS:
        {json.dumps(srs, indent=2)}

        SELECTED PATTERNS:
        {selected_patterns}

        STRUCTURAL RULES (You MUST follow these):
        {rules_str}

        INSTRUCTIONS:
        1. Generate a file tree with all necessary source code, config files, AND A 'tests/' DIRECTORY containing unit tests for the main components.
        2. Ensure code is high-quality, pythonic (if Python), and commented.
        3. [CRITICAL] For any entry point script (e.g., src/main.py, src/app.py), you MUST include the following code at the very top (before other imports) to ensure imports work correctly:
           import sys
           import os
           sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        4. Return ONLY a JSON object where keys are file paths (relative to project root) and values are file contents.
        
        Example Output:
        {{
            "src/main.py": "print('Hello')",
            "requirements.txt": "numpy"
        }}

        Do NOT wrap in markdown code blocks.
        """


        try:
            response_text = self.llm_client.generate_content(prompt)
            
            # Enhanced cleanup
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "")
            
            # Remove any leading/trailing whitespace
            response_text = response_text.strip()
            
            # Try parsing with strict=False first
            try:
                project_files = json.loads(response_text, strict=False)
            except json.JSONDecodeError as json_err:
                # More aggressive fix: use regex to properly escape newlines in JSON strings
                import re
                
                # This regex finds string values and escapes newlines within them
                def escape_newlines_in_strings(match):
                    string_content = match.group(1)
                    # Escape newlines, tabs, and carriage returns
                    string_content = string_content.replace('\\', '\\\\')
                    string_content = string_content.replace('\n', '\\n')
                    string_content = string_content.replace('\r', '\\r')
                    string_content = string_content.replace('\t', '\\t')
                    string_content = string_content.replace('"', '\\"')
                    return f'"{string_content}"'
                
                # Try to fix the JSON by escaping content within quotes
                # This is a simplified approach - find content between quotes and escape it
                try:
                    # Split by quotes and process alternating segments
                    parts = response_text.split('"')
                    fixed_parts = []
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Inside quotes (string content)
                            # Escape special characters
                            part = part.replace('\\', '\\\\')
                            part = part.replace('\n', '\\n')
                            part = part.replace('\r', '\\r')
                            part = part.replace('\t', '\\t')
                        fixed_parts.append(part)
                    
                    fixed_text = '"'.join(fixed_parts)
                    project_files = json.loads(fixed_text, strict=False)
                    
                except (json.JSONDecodeError, Exception) as e2:
                    # Last resort: return error
                    return {
                        "success": False, 
                        "error": f"JSON parsing failed: {str(json_err)}", 
                        "raw_response": response_text[:500]
                    }
            
            # Simple Validation
            validation_errors = self._validate_structure(project_files, selected_patterns)
            
            return {
                "success": True, 
                "files": project_files, 
                "validation_errors": validation_errors
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_structure(self, files: dict, patterns: list) -> list:
        errors = []
        for pattern in patterns:
            if pattern not in self.templates:
                continue
            
            req_structure = self.templates[pattern].get("required_structure", [])
            conventions = self.templates[pattern].get("file_conventions", [])

            # Check folders/paths
            for req in req_structure:
                found = any(req in path for path in files.keys())
                if not found:
                    errors.append(f"Pattern '{pattern}' requires folder/component '{req}' but none found.")
            
            # Check file conventions
            for conv in conventions:
                found = any(conv in path for path in files.keys())
                if not found:
                    errors.append(f"Pattern '{pattern}' requires files ending in '{conv}' but none found.")
        
        return errors
