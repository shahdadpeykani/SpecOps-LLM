"""
Pipeline Orchestrator for SpecOps.
Handles the execution flow from Prompt to SRS to Code Generation.
"""
import os
import shutil
from src.agents.spec_parser import SpecParser
from src.agents.pattern_selector import PatternSelector
from src.agents.code_generator import CodeGenerator
from src.agents.asset_generator import AssetGenerator
from src.tools.quality_runner import QualityRunner
from src.explainability.explainer import Explainer

class PipelineOrchestrator:
    def __init__(self):
        self.spec_parser = SpecParser()
        self.pattern_selector = PatternSelector()
        self.code_generator = CodeGenerator()
        self.asset_generator = AssetGenerator()
        self.quality_runner = QualityRunner()
        self.explainer = Explainer()
        self.generated_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../generated_projects'))

    def run_pipeline(self, prompt: str, step_callback=None):
        """
        Executes the full pipeline:
        Prompt -> SRS -> RAG -> Pattern Selection -> Code Gen -> Assets -> Git -> Quality Check -> Explain
        """
        print(f"Received prompt: {prompt}")
        
        
        # Step 1: SRS Parsing
        print("Step 1: Parsing SRS...")
        parse_result = self.spec_parser.parse_input(prompt)
        if not parse_result.get("success"):
            return self._error_response("SRS Parsing", parse_result)
        srs = parse_result["srs"]
        if step_callback: step_callback()

        # Step 2: Pattern Selection
        print("Step 2: Selecting Patterns (RAG)...")
        pattern_result = self.pattern_selector.select_patterns(srs)
        if not pattern_result.get("success"):
             return self._error_response("Pattern Selection", pattern_result, srs=srs)
        selected_patterns = pattern_result["selected_patterns"]
        candidates_count = pattern_result.get("retrieved_patterns_count", 0)
        if step_callback: step_callback()

        # Step 3: Code Generation
        print("Step 3: Generating Code...")
        code_result = self.code_generator.generate_code(srs, selected_patterns)
        if not code_result.get("success"):
            return self._error_response("Code Generation", code_result, srs=srs, patterns=selected_patterns)
        files = code_result["files"]
        validation_errors = code_result["validation_errors"]
        if step_callback: step_callback()

        # Step 4: Asset Generation
        print("Step 4: Generating Assets...")
        assets = self.asset_generator.generate_assets(srs, srs.get("tech_stack", []))
        files.update(assets)

        # Write files (Side Effect)
        project_name = srs.get("project_name", "SpecOpsProject").replace(" ", "_")
        project_path = os.path.join(self.generated_root, project_name)
        self._write_project_files(project_path, files)
        
        # Step 5: Git Initialization
        print("Step 5: Initializing Git...")
        git_success = self.asset_generator.initialize_git(project_path)

        # Step 6: Quality Checks & Self-Healing
        print("Step 6: Running Quality Gates & Self-Healing...")
        
        from src.agents.code_fixer import CodeFixer
        code_fixer = CodeFixer()
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            quality_report = self.quality_runner.run_all_checks(project_path)
            pylint_score = quality_report.get('pylint_score', 0)
            
            # Simple heuristic: If score is low, try to fix
            if pylint_score >= 6.0:
                print(f"  Quality passed (Score: {pylint_score}).")
                break
            
            if attempt < max_retries:
                print(f"  Quality score low ({pylint_score}). Attempting Self-Healing ({attempt+1}/{max_retries})...")
                
                # 1. Get detailed error log
                pylint_log = self.quality_runner.get_pylint_report(project_path)
                
                # 2. Parse log to find failing files
                # Simple parsing: find lines starting with file path inside project
                import re
                # Regex to capture filename from pylint output: "src/main.py:10:4: E0602..."
                # We look for paths relative to project root
                errors_by_file = {}
                for line in pylint_log.splitlines():
                    if "E" in line or "F" in line: # Error or Fatal
                         parts = line.split(':')
                         if len(parts) >= 3:
                             rel_path = parts[0].strip()
                             # Check if it's a python file in our project
                             full_file_path = os.path.join(project_path, rel_path)
                             if os.path.exists(full_file_path) and rel_path.endswith('.py'):
                                 if full_file_path not in errors_by_file:
                                     errors_by_file[full_file_path] = []
                                 errors_by_file[full_file_path].append(line)
                
                if not errors_by_file:
                    print("  No parseable errors found to fix.")
                    break
                
                # 3. Fix each failing file
                for file_path, errors in errors_by_file.items():
                    print(f"    Fixing {os.path.basename(file_path)}...")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        fix_result = code_fixer.fix_code(file_path, content, "\n".join(errors))
                        
                        if fix_result["success"]:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(fix_result["fixed_content"])
                            print(f"    Fixed {os.path.basename(file_path)}.")
                            
                            # Update our internal file map to reflect change (for explainability/history)
                            rel_path = os.path.relpath(file_path, project_path)
                            # Normalization usually needed but simple relative path works
                            if rel_path in files: 
                               files[rel_path] = fix_result["fixed_content"]
                            else:
                                # Try matching with os.sep differences or just basename matches?
                                # For now simple update if key exists matches rel_path
                                pass

                        else:
                            print(f"    Failed to fix {os.path.basename(file_path)}: {fix_result.get('error')}")
                    except Exception as e:
                        print(f"    Error processing {os.path.basename(file_path)}: {e}")
            else:
                print("  Max self-healing retries reached.")

        # Step 7: Explainability
        print("Step 7: Generating Explanation...")
        explanation = self.explainer.generate_explanation(srs, selected_patterns, quality_report)

        # Save to History
        from src.backend.history_manager import HistoryManager
        history_mgr = HistoryManager()
        history_mgr.save_project_entry({
            "project_name": srs.get("project_name", "Unknown"),
            "prompt": prompt,
            "path": project_path,
            "srs": srs
        })

        return {
            "status": "Completed", 
            "stage": "Pipeline Finished",
            "srs": srs,
            "patterns": selected_patterns,
            "project_path": project_path,
            "validation_errors": validation_errors,
            "file_count": len(files),
            "git_initialized": git_success,
            "quality_report": quality_report,
            "explanation": explanation,
            "retrieved_patterns_count": candidates_count
        }

    def _write_project_files(self, base_path: str, files: dict):
        if os.path.exists(base_path):
            try:
                shutil.rmtree(base_path)
            except Exception:
                pass 
        os.makedirs(base_path, exist_ok=True)
        for rel_path, content in files.items():
            # Ensure path is relative by stripping leading slashes/backslashes
            rel_path = rel_path.lstrip('/\\')
            full_path = os.path.join(base_path, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def _error_response(self, stage, result, **kwargs):
        return {
            "status": "Failed",
            "stage": stage,
            "error": result.get("error"),
            "details": result,
            **kwargs
        }
