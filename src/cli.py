"""
CLI Entry Point for SpecOps.
"""
import argparse
import sys
import os

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.pipeline_orchestrator import PipelineOrchestrator

def main():
    parser = argparse.ArgumentParser(description="SpecOps CLI")
    parser.add_argument("prompt", help="Input prompt for code generation")
    args = parser.parse_args()

    orchestrator = PipelineOrchestrator()
    result = orchestrator.run_pipeline(args.prompt)
    print(result)

if __name__ == "__main__":
    main()
