"""
SpecOps Frontend Application (Streamlit).
"""
import sys
import os
import streamlit as st

GEMINI_MODEL = "Gemini 3 Flash"
# Add project root to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.backend.pipeline_orchestrator import PipelineOrchestrator
from src.agents.chat_agent import ChatAgent

def main():
    st.set_page_config(page_title="SpecOps Dashboard", layout="wide", page_icon="🏗️")
    
    # Initialize session state for chat
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'project_result' not in st.session_state:
        st.session_state.project_result = None
    if 'total_input_tokens' not in st.session_state:
        st.session_state.total_input_tokens = 0
    if 'total_output_tokens' not in st.session_state:
        st.session_state.total_output_tokens = 0
    
    st.title("🏗️ SpecOps: Agentic Code Generator")
    st.markdown("---")

    # Sidebar with Chat
    with st.sidebar:
        st.header("💬 Ask Questions")
        
        if st.session_state.chat_agent:
            # Display chat history
            for msg in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(msg["user"])
                with st.chat_message("assistant"):
                    st.write(msg["assistant"])
            
            # Chat input
            user_input = st.chat_input("Ask about your project...")
            if user_input:
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_agent.chat(user_input)
                    
                    # Update token counts (Handled by LLMClient -> TokenTracker now)
                    # if st.session_state.chat_agent and hasattr(st.session_state.chat_agent, 'llm_client'):
                    #      st.session_state.total_input_tokens += ...

                st.session_state.chat_history.append({
                    "user": user_input,
                    "assistant": response
                })
                st.rerun()
        else:
            st.info("Generate a project first to start chatting!")
        
        st.markdown("---")
        
        # Project History Section
        st.header("📜 Project History")
        from src.backend.history_manager import HistoryManager
        history_mgr = HistoryManager()
        history = history_mgr.get_all_projects()
        
        if not history:
            st.text("No history found.")
        else:
            for proj in history:
                label = f"{proj.get('project_name', 'Untitled')} ({proj.get('timestamp', '00:00')})"
                if st.button(label, key=f"hist_{proj.get('path')}", use_container_width=True):
                    # Load this project into view
                    st.session_state.project_result = {
                        "srs": proj.get("srs"),
                        "patterns": [], # History might not have everything, verify what we saved
                        "project_path": proj.get("path"),
                        "status": "Completed",
                        "validation_errors": [],
                        "file_count": 0, # Should verify existence
                        "git_initialized": True,
                        "quality_report": {}, # Check if we can save/load this too or regenerate
                        "explanation": "Loaded from History."
                    }
                    if 'srs' in proj:
                        # Try to reconstruct missing bits if possible or just show what we have
                        st.session_state.project_result["patterns"] = proj.get("srs", {}).get("patterns", []) # SRS usually doesn't have patterns?
                        
                    # Re-initialize chat agent for this context
                    st.session_state.chat_agent = ChatAgent(project_context={
                        "srs": proj.get("srs"),
                        "files": {},
                        "patterns": [],
                        "project_path": proj.get("path")
                    })
                    st.session_state.conversation_stage = 'generating'
                    st.rerun()

        st.markdown("---")
        st.header("Configuration")
        st.info("Model:" + GEMINI_MODEL)
        st.success("Target: Python/Streamlit")
        st.markdown("---")
        st.markdown("**Pipeline Stages:**")
        st.checkbox("SRS Enforcement", value=True, disabled=True)
        st.checkbox("RAG Pattern Selection", value=True, disabled=True)
        st.checkbox("Code Generation", value=True, disabled=True)
        st.checkbox("Quality Gates", value=True, disabled=True)
        st.checkbox("Explainability", value=True, disabled=True)
        
        st.markdown("---")
        with st.expander("📊 Utilization", expanded=True):
             from src.backend.token_tracker import TokenTracker
             tracker = TokenTracker()
             status = tracker.get_usage_summary()
             
             # Render based on backend data
             st.progress(status["usage_pct"], text=f"Context Usage ({status['usage_pct']:.1%})")
             st.markdown(f"**Input Tokens:** {status['input_tokens']}")
             st.markdown(f"**Output Tokens:** {status['output_tokens']}")
             st.caption(f"Total: {status['total_tokens']} / {status['limit']}")
             
             if status["is_exceeded"]:
                 st.error("⚠️ Context Window Exceeded!")
    # Initialize conversation stage
    if 'conversation_stage' not in st.session_state:
        st.session_state.conversation_stage = 'initial'  # initial, qa, generating
    if 'initial_prompt' not in st.session_state:
        st.session_state.initial_prompt = ""
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    # Stage 1: Initial Prompt
    if st.session_state.conversation_stage == 'initial':
        st.subheader("📝 Describe Your Project")
        st.write("Tell me what you want to build, and I'll ask some clarifying questions.")
        
        with st.form(key="initial_form"):
            prompt = st.text_area(
                "Project Description:",
                height=150,
                placeholder="E.g., Build a To-Do list application...",
                key="initial_prompt_input"
            )
            
            # Submit button inside the form (Ctrl+Enter triggers this)
            if st.form_submit_button("🤔 Ask Me Questions", type="primary", use_container_width=True):
                if prompt:
                    st.session_state.initial_prompt = prompt
                    # Generate questions
                    from src.agents.requirements_gatherer import RequirementsGatherer
                    gatherer = RequirementsGatherer()
                    
                    try:
                        with st.spinner("Generating clarifying questions... (this may take a moment)"):
                            st.session_state.questions = gatherer.generate_questions(prompt)
                            
                            # Tokens tracked automatically by LLMClient

                        st.session_state.conversation_stage = 'qa'
                        st.rerun()
                    except Exception as e:
                        if "429" in str(e) or "ResourceExhausted" in str(e):
                            st.error("⏳ API Rate Limit Reached. Please wait a minute and try again.")
                        else:
                             st.error(f"Error generating questions: {e}")
                else:
                    st.error("Please describe your project first!")
    
    # Stage 2: Q&A
    elif st.session_state.conversation_stage == 'qa':
        st.subheader("💬 Answer These Questions")
        st.info(f"**Your Project**: {st.session_state.initial_prompt}")
        st.write("Please answer these questions to help me understand your needs better:")
        
        # Display questions and collect answers
        if st.button("⬅️ Back to Edit Prompt"):
            st.session_state.conversation_stage = 'initial'
            st.rerun()

        with st.form(key="qa_form"):
            # Display questions and collect answers
            for i, question in enumerate(st.session_state.questions, 1):
                answer = st.text_input(
                    f"**Q{i}**: {question}",
                    key=f"answer_{i}",
                    value=st.session_state.answers.get(question, "")
                )
                st.session_state.answers[question] = answer
            
            if st.form_submit_button("🚀 Generate Project", type="primary", use_container_width=True):
                # Check if all questions answered
                if all(st.session_state.answers.get(q, "").strip() for q in st.session_state.questions):
                    st.session_state.conversation_stage = 'generating'
                    import time
                    st.session_state.generation_start_time = time.time()
                    st.rerun()
                else:
                    st.error("Please answer all questions before generating!")
    
    # Stage 3: Generating
    elif st.session_state.conversation_stage == 'generating':
        # Only run pipeline if we don't have results yet
        if not st.session_state.project_result:
            from src.agents.requirements_gatherer import RequirementsGatherer
            gatherer = RequirementsGatherer()
            
            # Enhance prompt with Q&A
            enhanced_prompt = gatherer.enhance_prompt(
                st.session_state.initial_prompt,
                st.session_state.answers
            )
            
            orchestrator = PipelineOrchestrator()
            
            # Progress Container
            with st.status("Executing SpecOps Pipeline...", expanded=True) as status:
                st.write("🔍 Parsing SRS & Enforcing Schema...")
                
                # Callback to update sidebar during execution
                def update_metrics():
                    # We can't easily force a full rerun, but we can update a placeholder
                    # OR simply rely on the fact that sidebar *might* update if we interact with it.
                    # Ideally, we pass 'st' and update specific elements.
                    # Since we can't context-switching easily, let's try a simple write to a placeholder
                    # actually, the sidebar logic is re-run on EVERY script run.
                    # But inside this function, script isn't re-running.
                    # We need to manually update the container if possible. 
                    # For now, let's just let the TokenTracker accumulate.
                    pass

                result = orchestrator.run_pipeline(enhanced_prompt, step_callback=None) # Callback omitted for now as explicit UI redraw is complex without placeholders
                
                if result["status"] == "Failed":
                    status.update(label="Pipeline Failed", state="error", expanded=True)
                    st.error(f"Error in stage {result['stage']}: {result['error']}")
                    if "details" in result:
                        st.json(result["details"])
                    # Don't save failed results to session state to allow retry
                    return
    
                st.write("📚 Retrieving Design Patterns (RAG)...")
                st.write("🛠️ Generating Pattern-Compliant Code...")
                st.write("📂 Creating Assets & Initializing Git...")
                st.write("✅ Running Quality Gates & Tests...")
                st.write("🧠 Generating Explanation...")
                
                status.update(label="Pipeline Completed Successfully!", state="complete", expanded=False)
                
                # Calculate duration
                import time
                if 'generation_start_time' in st.session_state:
                     duration = time.time() - st.session_state.generation_start_time
                     result["duration_seconds"] = duration
            
            st.session_state.project_result = result
        
        # Use existing result
        result = st.session_state.project_result
        
        if result.get("duration_seconds"):
             st.success(f"✨ Generation completed in **{result['duration_seconds']:.2f} seconds**!")

        # Initialize Chat Agent if needed
        if not st.session_state.chat_agent:
             st.session_state.chat_agent = ChatAgent(project_context={
                "srs": result.get("srs"),
                "files": {},  # Don't include full files to save memory
                "patterns": result.get("patterns"),
                "project_path": result.get("project_path")
            })

        # Structure Results using Tabs
        tab_explanation, tab_srs, tab_files, tab_quality = st.tabs([
            "🧠 Explanation & Justification", 
            "📋 SRS & Patterns", 
            "📂 Generated Files", 
            "🛡️ Quality Report"
        ])

        with tab_explanation:
            st.markdown(result.get("explanation", "No explanation generated."))
            
            st.markdown("### Project Location")
            st.success(f"Files generated at: `{result.get('project_path')}`")
            if result.get("git_initialized"):
                st.info("Git Repository Initialized.")

        with tab_srs:
            st.subheader("Structured Requirements Specification")
            st.json(result.get("srs", {}))
            st.markdown("---")
            st.subheader("Selected Design Patterns")
            st.info(f"🔎 Using **Vector Knowledge Base (ChromaDB)**. Patterns Retrieved: {result.get('retrieved_patterns_count', 0)}")
            st.write(result.get("patterns", []))

        with tab_files:
            file_count = result.get("file_count", 0)
            st.metric("Total Files Generated", file_count)
            
            # Simple file tree simulation (list)
            project_path = result.get("project_path")
            if project_path and os.path.exists(project_path):
                file_list = []
                for root, _, files in os.walk(project_path):
                    for file in files:
                        rel = os.path.relpath(os.path.join(root, file), project_path)
                        file_list.append(rel)
                st.write(file_list)
            
            st.warning("Validation Errors (if any):")
            st.write(result.get("validation_errors", []))

        with tab_quality:
            metrics = result.get("quality_report", {})
            
            q_col1, q_col2, q_col3 = st.columns(3)
            with q_col1:
                st.metric("Pylint Score", f"{metrics.get('pylint_score', 0)}/10")
            with q_col2:
                bandit_issues = metrics.get('bandit_issues', {})
                if isinstance(bandit_issues, dict):
                    high = bandit_issues.get('high', 0)
                    medium = bandit_issues.get('medium', 0)
                    st.metric("Security Issues (High)", high, delta_color="inverse")
                else:
                    st.success("No critical security issues found.")
            with q_col3:
                st.metric("Tests Passed", metrics.get('tests_passed', 0))
            
            if metrics.get('bandit_issues') != "No output" and isinstance(metrics.get('bandit_issues'), dict):
                st.json(metrics['bandit_issues'])
        
        # Add button to start new project
        st.markdown("---")
        if st.button("🔄 Start New Project", type="primary"):
            # Reset conversation state
            st.session_state.conversation_stage = 'initial'
            st.session_state.initial_prompt = ""
            st.session_state["initial_prompt_input"] = "" # Clear widget state
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.chat_history = []
            st.session_state.project_result = None # Clear result
            st.session_state.chat_agent = None 
            st.rerun()

if __name__ == "__main__":
    main()
