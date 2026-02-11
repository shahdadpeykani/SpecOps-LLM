"""
History Manager Module.
Handles persistence of generated projects to a JSON file.
"""
import json
import os
import time
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file: str = "data/history.json"):
        # Resolve path relative to project root (assuming this file is in src/backend)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.history_file = os.path.join(base_dir, history_file)
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Creates the history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def save_project_entry(self, project_data: dict):
        """
        Saves a new project entry to the history file.
        
        Args:
            project_data: Dict containing 'project_name', 'prompt', 'path', 'srs', 'timestamp'
        """
        try:
            # Load existing
            history = self.get_all_projects()
            
            # Add timestamp if missing
            if 'timestamp' not in project_data:
                project_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            # Prepend to list (newest first)
            history.insert(0, project_data)
            
            # Save
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Failed to save history: {e}")
            return False

    def get_all_projects(self) -> list:
        """
        Returns list of all projects that actually exist on disk.
        Removes missing projects from the history file.
        """
        try:
            if not os.path.exists(self.history_file):
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Filter valid projects
            valid_history = []
            changes_made = False
            
            for proj in history:
                path = proj.get('path')
                if path and os.path.exists(path):
                    valid_history.append(proj)
                else:
                    changes_made = True
            
            # Update file if we pruned anything
            if changes_made:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(valid_history, f, indent=2)
                    
            return valid_history
        except Exception:
            return []

    def clear_history(self):
        """Clears the history file."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
