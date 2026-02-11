🚀 SpecOps – Pattern-Compliant Code Generation with RAG & Self-Healing

SpecOps is an AI-powered framework that transforms natural language prompts into architecturally structured, quality-validated Python projects.
Unlike generic LLM code generators, SpecOps enforces software engineering discipline using Retrieval-Augmented Generation (RAG) and an automated self-healing loop.

🎯 What Problem Does It Solve?
LLM-based code tools often:
-Generate unstructured projects
-Hallucinate design patterns
-Produce low-quality or broken code

SpecOps ensures:
📄 Structured SRS generation
🧠 RAG-grounded pattern selection
🏗 Pattern-compliant architecture
🔁 Automatic quality validation & repair

🏗 How It Works
1️⃣ Specification Parsing
Free-text prompt → Structured SRS (JSON)

2️⃣ RAG-Based Pattern Selection
Uses ChromaDB
Searches real PDF documentation of design patterns:
-MVC
-Repository
-Factory
-Observer
-Service Layer
-Singleton
Prevents architectural hallucinations.

3️⃣ Code Generation
Generates a complete Python project:
-Source code
-Tests
-README
-requirements.txt

4️⃣ Self-Healing Quality Loop
Runs Pylint
Enforces minimum score: ≥ 6.0
If below threshold → CodeFixer rewrites code (max 2 retries)
This turns SpecOps into a reliable AI development assistant, not just a generator.

⚙️ Tech Stack
-Python 3.12
-Google Gemini API
-ChromaDB (vector database)
-Pylint (static analysis)
-Streamlit (UI)

🧪 Example
Prompt:
Build a Student Management System

Pipeline:
SpecParser → PatternSelector (MVC + Repository) → CodeGenerator → CodeFixer

Output:
A zipped, structured, pattern-compliant Python project.

📊 Evaluation
✅ Success metric: Pylint score ≥ 6.0
✅ RAG grounded in real pattern PDFs
🔄 CodeFixer improved scores from 4.0 → 8.0 during testing

👥 Team
Shahdad Peykani 
Muhammad Ozar Mirza 
Abdirahman T. F. Hussein 

Developed for CMPE 472 – Large Language Models (2026).
