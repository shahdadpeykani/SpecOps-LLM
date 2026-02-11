# 🚀 SpecOps – Pattern-Compliant Code Generation with RAG & Self-Healing

SpecOps is an AI-powered framework that transforms natural language prompts into **architecturally structured, quality-validated Python projects**.

Unlike generic LLM code generators, SpecOps enforces software engineering discipline using **Retrieval-Augmented Generation (RAG)** and an automated **self-healing quality loop**.

---

## 🎯 Problem

LLM-based code generation tools often:

- Generate unstructured projects  
- Hallucinate architectural patterns  
- Produce low-quality or non-executable code  

SpecOps ensures:

- 📄 Structured SRS generation  
- 🧠 RAG-grounded design pattern selection  
- 🏗 Pattern-compliant architecture  
- 🔁 Automatic quality validation & repair  

---

## 🏗 How It Works

### 1️⃣ Specification Parsing
Free-text prompt → Structured Software Requirements Specification (SRS JSON)

### 2️⃣ RAG-Based Pattern Selection
- Uses **ChromaDB** vector database  
- Searches real PDF documentation of design patterns:
  - MVC  
  - Repository  
  - Factory  
  - Observer  
  - Service Layer  
  - Singleton  

This prevents architectural hallucination and enforces grounded decisions.

### 3️⃣ Code Generation
Generates a complete Python project including:

- Source code  
- Tests  
- README  
- requirements.txt  

### 4️⃣ Self-Healing Quality Loop
- Runs **Pylint** static analysis  
- Enforces minimum score: **≥ 6.0**  
- If below threshold → CodeFixer rewrites code (max 2 retries)  

This transforms SpecOps into a **reliable AI development assistant**, not just a generator.

---

## ⚙️ Tech Stack

- Python 3.12  
- Google Gemini API  
- ChromaDB (Vector Database)  
- Pylint (Static Analysis)  
- Streamlit (UI)  

---

## 🧪 Example

**Prompt**

**Pipeline**
SpecParser → PatternSelector (MVC + Repository) → CodeGenerator → CodeFixer  

**Output**
A zipped, structured, pattern-compliant Python project.

---

## 📊 Evaluation

- ✅ Success Metric: Pylint score ≥ 6.0  
- ✅ RAG grounded in academic pattern PDFs  
- 🔄 CodeFixer improved scores from 4.0 → 8.0 during testing  

---

## 👥 Team

- Shahdad Peykani  
- Muhammad Ozar Mirza 
- Abdirahman T. F. Hussein 

---

Developed for **CMPE 472 – Large Language Models (2026)**.
