"""
Chat Agent for SpecOps.
Provides conversational interface to answer questions about generated projects.
"""
import json
from src.backend.llm_client import LLMClient

class ChatAgent:
    def __init__(self, project_context: dict = None):
        """
        Initialize chat agent with project context.
        
        Args:
            project_context: Dictionary containing:
                - srs: Software Requirements Specification
                - files: Generated code files (dict of filename: content)
                - patterns: Selected design patterns
                - project_path: Path to generated project
        """
        self.llm_client = LLMClient()
        self.project_context = project_context or {}
        self.conversation_history = []
    
    def chat(self, user_message: str) -> str:
        """
        Respond to user question with project context.
        
        Args:
            user_message: User's question or message
            
        Returns:
            Assistant's response
        """
        # Build context-aware prompt
        context_prompt = self._build_context_prompt()
        
        # Add conversation history
        history_prompt = self._format_history()
        
        # Generate response
        full_prompt = f"""{context_prompt}

{history_prompt}

User: {user_message}
Assistant:"""
        
        response = self.llm_client.generate_content(full_prompt)
        
        # Update history
        self.conversation_history.append({
            "user": user_message,
            "assistant": response
        })
        
        return response
    
    def _build_context_prompt(self) -> str:
        """Build prompt with project context."""
        if not self.project_context:
            return "You are a helpful coding assistant."
        
        srs = self.project_context.get('srs', {})
        files = self.project_context.get('files', {})
        patterns = self.project_context.get('patterns', [])
        
        # Build file list (just names, not full content to save tokens)
        file_list = list(files.keys()) if files else []
        
        context = f"""You are an expert coding assistant helping with a generated software project.

Project Details:
- Name: {srs.get('project_name', 'Unknown')}
- Description: {srs.get('description', 'No description')}
- Tech Stack: {', '.join(srs.get('tech_stack', []))}
- Design Patterns: {', '.join(patterns)}

Generated Files:
{chr(10).join(f'  - {f}' for f in file_list)}

Answer questions about this project accurately and helpfully. You can explain:
- How to run the project
- Code structure and architecture
- Design decisions and patterns used
- How to add new features
- Troubleshooting and debugging tips
"""
        return context
    
    def _format_history(self) -> str:
        """Format conversation history for prompt."""
        if not self.conversation_history:
            return ""
        
        # Limit to last 5 exchanges to manage token count
        recent_history = self.conversation_history[-5:]
        
        formatted = "Previous conversation:\\n"
        for exchange in recent_history:
            formatted += f"User: {exchange['user']}\\n"
            formatted += f"Assistant: {exchange['assistant']}\\n\\n"
        
        return formatted
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
