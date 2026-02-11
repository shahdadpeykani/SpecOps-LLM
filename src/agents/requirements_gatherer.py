"""
Requirements Gatherer Agent.
Generates clarifying questions based on initial prompt and enhances requirements.
"""
from src.backend.llm_client import LLMClient

class RequirementsGatherer:
    def __init__(self):
        self.llm_client = LLMClient()
    
    def generate_questions(self, initial_prompt: str) -> list:
        """
        Generate 5 clarifying questions based on initial prompt.
        
        Args:
            initial_prompt: User's initial project description
            
        Returns:
            List of 5 clarifying questions
        """
        prompt = f"""You are a software requirements analyst. A user wants to build a project with this description:

"{initial_prompt}"

Generate exactly 5 clarifying questions to better understand their requirements. Focus on:
1. Technical stack preferences
2. Specific features or functionality
3. Scale and complexity
4. User interface preferences
5. Integration or deployment needs

Return ONLY a JSON array of 5 questions, nothing else. Format:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]
"""
        
        try:
            response = self.llm_client.generate_content(prompt)
            
            # Clean up response
            response = response.strip()
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "")
            response = response.strip()
            
            # Parse JSON
            import json
            questions = json.loads(response)
            
            # Ensure we have exactly 5 questions
            if isinstance(questions, list) and len(questions) >= 5:
                return questions[:5]
            else:
                # Fallback questions
                return self._get_fallback_questions()
                
        except Exception as e:
            # Re-raise rate limit errors so frontend can handle them
            if "429" in str(e) or "ResourceExhausted" in str(e):
                raise e
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions()
    
    def enhance_prompt(self, initial_prompt: str, qa_pairs: dict) -> str:
        """
        Combine initial prompt with Q&A answers into detailed prompt.
        
        Args:
            initial_prompt: Original user prompt
            qa_pairs: Dictionary of {question: answer}
            
        Returns:
            Enhanced, detailed prompt
        """
        qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs.items()])
        
        enhanced = f"""Original Request:
{initial_prompt}

Additional Details from User:
{qa_text}

Please build a project that incorporates all of the above requirements and preferences."""
        
        return enhanced
    
    def _get_fallback_questions(self) -> list:
        """Fallback questions if LLM fails."""
        return [
            "What programming language or framework do you prefer?",
            "What are the main features you need in this project?",
            "How many users do you expect to support?",
            "Do you need a web interface, CLI, or API?",
            "Are there any specific libraries or tools you want to use?"
        ]
