"""
LexFusion Cross-Examine Debate Page
====================================
Immersive visual interface showing the multi-round courtroom debate
between Advocate A and Advocate B, concluding with a Judge synthesis.
"""

from __future__ import annotations

import streamlit as st
from utils.api_client import LexFusionAPIClient
from components.advocate_column import render_debate_rounds
from components.answer_card import render_synthesis_card, render_source_cards


def render_debate_page(client: LexFusionAPIClient):
    """Renders the adversarial debate page."""
    st.markdown(
        """
        <div class="title-banner">
            <h1 class="court-title" style="font-size: 2.4rem; margin-bottom: 8px;">
                🏛️ CROSS-EXAMINE <span class="gold-text">DEBATE CHAMBER</span>
            </h1>
            <p style="color: #9ca3af; font-size: 0.98rem; margin: 0; letter-spacing: 0.5px;">
                Multi-Agent Adversarial Debate • Prosecution vs. Defence • Automated Judicial Ruling
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar parameters for debate configuration
    st.sidebar.markdown("### 🎛️ Chamber Settings")
    debate_rounds = st.sidebar.slider("Debate Rounds", min_value=1, max_value=3, value=2)
    top_k = st.sidebar.slider("Evidence Retrieve Count (Top K)", min_value=3, max_value=10, value=5)

    # Input zone
    st.markdown("### ⚖️ File an Argument")
    user_query = st.text_area(
        "Define the legal issue/dispute to cross-examine:",
        placeholder="e.g., Is the vendor liable for damages if a data breach occurs due to a third-party API outage?",
        height=90,
    )

    if st.button("⚖️ Convene Courtroom", use_container_width=True):
        if not user_query.strip():
            st.warning("Please provide a legal query first.")
            return

        # Running indicator
        with st.status("Court is in session. Running Agentic Graph...", expanded=True) as status:
            status.update(label="Advocates preparing arguments...", state="running")
            
            # Execute debate
            response = client.query(
                query=user_query,
                debate_mode=True,
                top_k=top_k,
                max_rounds=debate_rounds,
            )

            if response.get("status") == "complete" or "synthesis" in response:
                status.update(label="Rulings delivered by Presiding Judge.", state="complete")
                
                # Render results in session state to persist
                st.session_state.active_debate = response
            else:
                status.update(label="Court session errored.", state="error")
                err_msg = response.get("error_message", "Execution failed.")
                st.error(f"Court session aborted: {err_msg}")

    # Display active debate results
    if "active_debate" in st.session_state:
        res = st.session_state.active_debate
        
        # Render the rounds of debate (Advocate A vs. Advocate B)
        render_debate_rounds(res.get("argument_history", []))
        
        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1); margin-top: 30px; margin-bottom: 30px;' />", unsafe_allow_html=True)
        
        # Render the Judge ruling and confidence gauge
        render_synthesis_card(
            synthesis=res.get("synthesis", "Synthesis finding missing."),
            confidence_score=res.get("confidence_score", 50),
        )

        st.markdown("<br />", unsafe_allow_html=True)

        # Render sources
        render_source_cards(res.get("source_documents", []))
