"""
SpecParser Agent.
Converts natural language prompts into structured SRS.
"""
import json
import os
import jsonschema
from src.backend.llm_client import LLMClient

class SpecParser:
    def __init__(self):
        self.llm_client = LLMClient()
        self.schema_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../data/schemas/srs_schema.json')
        )
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def parse_input(self, prompt: str) -> dict:
        """
        Parses input prompt to SRS using LLM and validates against schema.
        """
        system_prompt = f"""
        You are an expert Software Architect. Convert the following user request into a detailed Software Requirements Specification (SRS) JSON object.
        
        The JSON must strictly follow this schema:
        {json.dumps(self.schema, indent=2)}

        User Request: {prompt}

        Return ONLY the raw JSON. No markdown formatting.
        """

        try:
            response_text = self.llm_client.generate_content(system_prompt)
            # Basic cleanup if LLM returns markdown blocks
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "")
            
            srs_data = json.loads(response_text)
            
            # Validate against schema
            jsonschema.validate(instance=srs_data, schema=self.schema)
            
            return {"success": True, "srs": srs_data}
        
        except json.JSONDecodeError:
            return {"success": False, "error": "LLM returned invalid JSON", "raw_response": response_text}
        except jsonschema.ValidationError as e:
            return {"success": False, "error": f"Schema Validation Error: {e.message}", "srs": srs_data}
        except Exception as e:
            return {"success": False, "error": str(e)}
