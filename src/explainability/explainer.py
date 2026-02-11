"""
Explainer Module.
Provides justifications for patterns and traceability.
"""
import json
from src.backend.llm_client import LLMClient

class Explainer:
    def __init__(self):
        self.llm_client = LLMClient()

    def generate_explanation(self, srs: dict, selected_patterns: list, quality_report: dict) -> str:
        """
        Generates a natural language explanation of the design decisions.
        """
        prompt = f"""
        You are the SpecOps System Explainer. Review the following project details and provide a concise, professional explanation of the architectural choices.

        PROJECT SRS:
        {json.dumps(srs, indent=2)}

        SELECTED PATTERNS:
        {selected_patterns}

        QUALITY METRICS:
        {json.dumps(quality_report, indent=2)}

        INSTRUCTIONS:
        1. Explain WHY the selected patterns were chosen based on specific SRS requirements (Traceability).
        2. Summarize the code quality and security posture based on the metrics.
        3. Highlight any risks or trade-offs.
        
        Output formatted in Markdown.
        """

        try:
            explanation = self.llm_client.generate_content(prompt)
            return explanation
        except Exception as e:
            return f"Failed to generate explanation: {str(e)}"
