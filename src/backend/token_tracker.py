"""
Token Tracker Module.
Singleton to track token usage across the application.
"""

class TokenTracker:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenTracker, cls).__new__(cls)
            cls._instance.total_input_tokens = 0
            cls._instance.total_output_tokens = 0
        return cls._instance

    def add_input_tokens(self, count: int):
        self.total_input_tokens += count

    def add_output_tokens(self, count: int):
        self.total_output_tokens += count
    
    MAX_CONTEXT = 100_000

    def get_stats(self):
        """Raw stats."""
        return {
            "input": self.total_input_tokens,
            "output": self.total_output_tokens,
            "total": self.total_input_tokens + self.total_output_tokens
        }

    def get_usage_summary(self):
        """Calculated usage summary for frontend."""
        total = self.total_input_tokens + self.total_output_tokens
        limit = self.MAX_CONTEXT
        pct = total / limit if limit > 0 else 0.0
        
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": total,
            "limit": limit,
            "usage_pct": min(pct, 1.0),
            "is_exceeded": total > limit
        }

    def reset(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
