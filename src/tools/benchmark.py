"""
Benchmark Tool for SpecOps.
Runs multiple scenarios to validate system performance and metrics.
"""
import sys
import os
import json
import time

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.backend.pipeline_orchestrator import PipelineOrchestrator

SCENARIOS = [
    {
        "name": "E-commerce Backend",
        "prompt": "Build a scalable e-commerce backend with product search, shopping cart, and user authentication using the Repository pattern and Service layer."
    },
    {
        "name": "Personal Blog Engine",
        "prompt": "Create a simple blog engine where users can post articles and comment. Use MVC pattern."
    },
    {
        "name": "Todo List API",
        "prompt": "A lightweight REST API for a Todo list application. Use Singleton for database connection."
    }
]

def run_benchmark():
    orchestrator = PipelineOrchestrator()
    results = []
    
    print(f"Starting Benchmark on {len(SCENARIOS)} scenarios...")
    print("-" * 60)

    for scenario in SCENARIOS:
        print(f"Running Scenario: {scenario['name']}...")
        start_time = time.time()
        
        try:
            output = orchestrator.run_pipeline(scenario['prompt'])
            duration = time.time() - start_time
            
            success = output.get("status") == "Completed"
            quality = output.get("quality_report", {})
            file_count = output.get("file_count", 0)
            
            # Metrics
            pylint_score = quality.get("pylint_score", 0)
            tests_passed = quality.get("tests_passed", 0)
            
            # Validation Logic
            passed = success and pylint_score >= 5.0 and file_count > 0
            
            results.append({
                "scenario": scenario['name'],
                "success": success,
                "duration_sec": round(duration, 2),
                "files_generated": file_count,
                "pylint_score": pylint_score,
                "tests_passed": tests_passed,
                "overall_pass": passed
            })
            
            print(f"  -> Result: {'PASS' if passed else 'FAIL'}")
            
        except Exception as e:
            print(f"  -> CRITICAL ERROR: {e}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e),
                "overall_pass": False
            })

    print("-" * 60)
    print("Benchmark Complete. Summary:")
    print(json.dumps(results, indent=2))
    
    # Calculate Overall Success Rate
    total = len(results)
    passed_count = sum(1 for r in results if r["overall_pass"])
    print(f"\nSuccess Rate: {passed_count}/{total} ({passed_count/total*100:.1f}%)")

if __name__ == "__main__":
    run_benchmark()
