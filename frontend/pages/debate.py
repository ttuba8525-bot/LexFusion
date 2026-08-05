import streamlit as st
import time
from frontend.components.advocate_column import render_advocate_card, render_judge_verdict_card
from frontend.utils import api_client

# Helper function to render character nodes dashboard
def render_courtroom_dashboard(stage: str):
    """
    Renders a visual dashboard showing Arbiter Solomon, Aegis, and Ignis in different states.
    Stages: 'ready', 'advocate_a', 'advocate_b', 'judge', 'completed'
    """
    nodes = {
        "aegis": "",
        "ignis": "",
        "solomon": ""
    }
    
    if stage == "advocate_a":
        nodes["aegis"] = "active"
    elif stage == "advocate_b":
        nodes["aegis"] = "completed"
        nodes["ignis"] = "active"
    elif stage == "judge":
        nodes["aegis"] = "completed"
        nodes["ignis"] = "completed"
        nodes["solomon"] = "active"
    elif stage == "completed":
        nodes["aegis"] = "completed"
        nodes["ignis"] = "completed"
        nodes["solomon"] = "completed"
        
    theme_class = "light-override-theme-active" if st.session_state.theme == "light" else ""
    
    html = f"""
    <div class="courtroom-dashboard {theme_class}">
        <div style="font-family: 'Cinzel', serif; color: var(--accent-gold); font-size: 0.95rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 5px;">🏛️ Tribunal In Session</div>
        
        <div class="court-node judge-node {nodes['solomon']}">
            <div class="character-avatar">⚖️</div>
            <div class="character-name">Arbiter Solomon</div>
            <div class="character-role">Supreme Judge</div>
        </div>
        
        <div class="court-advocates">
            <div class="court-node advocate-node-a {nodes['aegis']}">
                <div class="character-avatar">🛡️</div>
                <div class="character-name">Aegis</div>
                <div class="character-role">Advocate (Party A)</div>
            </div>
            
            <div class="vs-badge">VS</div>
            
            <div class="court-node advocate-node-b {nodes['ignis']}">
                <div class="character-avatar">⚔️</div>
                <div class="character-name">Ignis</div>
                <div class="character-role">Advocate (Party B)</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# 1. Page Header
st.markdown('<h1 class="legal-serif" style="font-size: 2.2rem; margin-top: 10px; margin-bottom: 5px;">Adversarial Legal Debate</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: var(--text-secondary); margin-bottom: 25px;">Pitches two opposing AI advocates against each other to interpret complex clauses. A neutral judge agent resolves the dispute with a formal synthesized verdict.</p>', unsafe_allow_html=True)

# 2. Check Document Status
if st.session_state.uploaded_doc is None:
    # Empty State for Debate Page
    st.markdown(
        """
        <div class="lex-empty-state">
            <div class="lex-empty-icon">⚖️</div>
            <h2 class="legal-serif" style="font-size: 1.6rem; color: var(--accent-gold); margin-bottom: 8px;">Adversarial Debate Workspace</h2>
            <p style="color: var(--text-secondary); max-width: 600px; margin: 0 auto 20px auto; font-size: 0.95rem; line-height: 1.6;">
                Adversarial debate requires an active legal document context. Please upload a PDF contract or load our pre-indexed merger agreement demo.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_demo, _ = st.columns([1, 2])
    with col_demo:
        if st.button("🚀 Load Demo Merger Agreement", key="debate_load_demo_btn", type="primary"):
            st.session_state.uploaded_doc = api_client.MOCK_DOCUMENTS["doc_merger_2026"]
            st.rerun()
            
else:
    # Document loaded: display debate setup panel
    doc = st.session_state.uploaded_doc
    st.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid var(--border-color); padding: 15px; border-radius: 6px; margin-bottom: 25px;">
            <span style="color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">Active Document Context:</span>
            <strong style="color: var(--accent-gold); font-family: 'Playfair Display', serif; font-size: 1rem; margin-left: 8px;">
                {doc.get('filename')} ({doc.get('pages')} pages)
            </strong>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Selection of Debate Topics
    predefined_topics = [
        "Change of Control: Does a merger with a subsidiary trigger the 50% voting stock clause?",
        "IP Indemnification: Does the exclusion for 'combination of products' apply to APIs?",
        "Custom Debate Topic..."
    ]
    
    selected_option = st.selectbox(
        "Select a clause interpretation or topic to debate:",
        options=predefined_topics,
        index=0
    )
    
    debate_topic = ""
    if selected_option == "Custom Debate Topic...":
        debate_topic = st.text_area(
            "Enter your custom debate question / clause query:",
            placeholder="e.g., Does the Force Majeure clause cover supplier bankruptcies due to economic downturns?",
            height=100
        )
    else:
        debate_topic = selected_option
        
    # Initialize page debate states
    if "current_debate_topic" not in st.session_state:
        st.session_state.current_debate_topic = None
    if "current_debate_result" not in st.session_state:
        st.session_state.current_debate_result = None
        
    # Render static dashboard when debate has not run yet or results match another topic
    if not st.session_state.current_debate_result or st.session_state.current_debate_topic != debate_topic:
        render_courtroom_dashboard("ready")

    # Run Debate Trigger
    initiate_debate = st.button("⚖️ Initiate Adversarial Debate", type="primary", use_container_width=True)
    
    if initiate_debate:
        if not debate_topic.strip():
            st.error("Please select or enter a valid topic for the debate.")
        else:
            # Reset active result
            st.session_state.current_debate_topic = debate_topic
            st.session_state.current_debate_result = None
            
            # 1. Pre-fetch final mock/RAG debate data immediately to render step-by-step
            temp_gen = api_client.run_debate_stream(debate_topic, doc["doc_id"])
            final_data = None
            for status_msg, d in temp_gen:
                if d is not None:
                    final_data = d
            
            # Setup Progress Card Placeholders
            progress_placeholder = st.empty()
            
            # Step 1: Aegis Active. Show A card, B placeholder, Judge placeholder
            with progress_placeholder:
                render_courtroom_dashboard("advocate_a")
                
                st.markdown(
                    """
                    <div class="sequential-progress-container">
                        <div style="font-family: 'Cinzel', serif; color: var(--accent-gold); font-size: 1.02rem; margin-bottom: 15px; font-weight: 700; letter-spacing: 0.05em;">⚖️ Tribunal In Session: Aegis opening case...</div>
                        <div class="sequential-step active">
                            <span class="step-bullet">1</span>
                            <span>Aegis (Party A Counsel) is formulating opening argument...</span>
                        </div>
                        <div class="sequential-step">
                            <span class="step-bullet">2</span>
                            <span>Ignis: Preparing counterargument...</span>
                        </div>
                        <div class="sequential-step">
                            <span class="step-bullet">3</span>
                            <span>Judge Solomon: Reviewing citations & drafting ruling...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col_adv_a, col_adv_b = st.columns(2)
                with col_adv_a:
                    render_advocate_card("A", "Advocate Aegis (Party A's Stance)", final_data.get("argument_a", ""))
                with col_adv_b:
                    st.markdown(
                        """
                        <div class="advocate-card advocate-card-b" style="opacity: 0.35; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 250px; border-style: dashed; border-width: 1px;">
                            <div class="character-avatar spinner" style="font-size: 2.2rem; animation: blink 1.5s infinite;">⚔️</div>
                            <div class="legal-serif" style="font-size: 1.1rem; margin-top: 12px; color: var(--text-secondary);">Ignis is preparing response...</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                st.markdown(
                    """
                    <div class="judge-ruling-card" style="opacity: 0.3; display: flex; flex-direction: column; align-items: center; justify-content: center; border-style: dashed; border-width: 1px; padding: 25px; margin-top: 25px; min-height: 120px;">
                        <div class="character-avatar" style="font-size: 2.2rem;">⚖️</div>
                        <div class="legal-serif" style="font-size: 1.15rem; color: var(--accent-gold); margin-top: 8px;">Arbiter Solomon is standing by...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            time.sleep(2.0)
            
            # Step 2: Ignis Active. Show A card, B card, Judge placeholder
            with progress_placeholder:
                render_courtroom_dashboard("advocate_b")
                
                st.markdown(
                    """
                    <div class="sequential-progress-container">
                        <div style="font-family: 'Cinzel', serif; color: var(--accent-gold); font-size: 1.02rem; margin-bottom: 15px; font-weight: 700; letter-spacing: 0.05em;">⚖️ Tribunal In Session: Ignis rebutting...</div>
                        <div class="sequential-step completed">
                            <span class="step-bullet">✓</span>
                            <span>Aegis: Completed opening argument for Party A.</span>
                        </div>
                        <div class="sequential-step active">
                            <span class="step-bullet">2</span>
                            <span>Ignis (Party B Counsel) is preparing rebuttal argument...</span>
                        </div>
                        <div class="sequential-step">
                            <span class="step-bullet">3</span>
                            <span>Judge Solomon: Reviewing citations & drafting ruling...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col_adv_a, col_adv_b = st.columns(2)
                with col_adv_a:
                    render_advocate_card("A", "Advocate Aegis (Party A's Stance)", final_data.get("argument_a", ""))
                with col_adv_b:
                    render_advocate_card("B", "Advocate Ignis (Party B's Stance)", final_data.get("argument_b", ""))
                
                st.markdown(
                    """
                    <div class="judge-ruling-card" style="opacity: 0.3; display: flex; flex-direction: column; align-items: center; justify-content: center; border-style: dashed; border-width: 1px; padding: 25px; margin-top: 25px; min-height: 120px;">
                        <div class="character-avatar" style="font-size: 2.2rem;">⚖️</div>
                        <div class="legal-serif" style="font-size: 1.15rem; color: var(--accent-gold); margin-top: 8px;">Arbiter Solomon is standing by...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            time.sleep(2.0)
            
            # Step 3: Solomon Active. Show A card, B card, Judge loading/analyzing
            with progress_placeholder:
                render_courtroom_dashboard("judge")
                
                st.markdown(
                    """
                    <div class="sequential-progress-container">
                        <div style="font-family: 'Cinzel', serif; color: var(--accent-gold); font-size: 1.02rem; margin-bottom: 15px; font-weight: 700; letter-spacing: 0.05em;">⚖️ Tribunal In Session: Solomon rendering ruling...</div>
                        <div class="sequential-step completed">
                            <span class="step-bullet">✓</span>
                            <span>Aegis: Completed opening argument for Party A.</span>
                        </div>
                        <div class="sequential-step completed">
                            <span class="step-bullet">✓</span>
                            <span>Ignis: Completed rebuttal argument for Party B.</span>
                        </div>
                        <div class="sequential-step active">
                            <span class="step-bullet">3</span>
                            <span>Arbiter Solomon is weighing citations & synthesizing final verdict...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col_adv_a, col_adv_b = st.columns(2)
                with col_adv_a:
                    render_advocate_card("A", "Advocate Aegis (Party A's Stance)", final_data.get("argument_a", ""))
                with col_adv_b:
                    render_advocate_card("B", "Advocate Ignis (Party B's Stance)", final_data.get("argument_b", ""))
                
                st.markdown(
                    """
                    <div class="judge-ruling-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 25px; margin-top: 25px; min-height: 120px; border-color: var(--accent-gold); box-shadow: 0 0 15px var(--accent-gold-glow);">
                        <div class="character-avatar spinner" style="font-size: 2.2rem; animation: blink 1.4s infinite;">⚖️</div>
                        <div class="legal-serif" style="font-size: 1.2rem; color: var(--accent-gold); margin-top: 8px; font-weight: 600;">Arbiter Solomon is writing the final ruling...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            time.sleep(2.0)
            
            # Step 4: Finished. Clear progress and write results to state
            progress_placeholder.empty()
            st.session_state.current_debate_result = final_data
            st.rerun()

    # 3. Display active debate results
    if st.session_state.current_debate_result and st.session_state.current_debate_topic == debate_topic:
        res = st.session_state.current_debate_result
        
        # Display completed courtroom dashboard above results
        render_courtroom_dashboard("completed")
        
        # Section Header for Debate
        st.markdown(
            f"""
            <div style="margin-top: 30px; margin-bottom: 20px; border-left: 3px solid var(--accent-gold); padding-left: 10px;">
                <span style="color: var(--text-secondary); font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">Active Debate Topic</span>
                <h3 class="legal-serif" style="margin: 0; color: var(--text-primary); font-size: 1.3rem;">{st.session_state.current_debate_topic}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Side-by-Side Advocate Columns
        col_adv_a, col_adv_b = st.columns(2)
        
        with col_adv_a:
            render_advocate_card(
                side="A",
                title="Advocate Aegis (Party A's Stance)",
                argument_text=res.get("argument_a", "")
            )
            
        with col_adv_b:
            render_advocate_card(
                side="B",
                title="Advocate Ignis (Party B's Stance)",
                argument_text=res.get("argument_b", "")
            )
            
        # Judge Synthesized Verdict Card below
        render_judge_verdict_card(res.get("verdict", {}))
