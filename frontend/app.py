"""
LexFusion — Primary Streamlit Application Entry Point
======================================================
Combines subpages, sidebar parameters, custom styling,
and file uploading with premium UI assets.
"""

from __future__ import annotations

import os
import sys
import streamlit as st

# Setup paths to ensure we can load utilities cleanly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.api_client import LexFusionAPIClient
from pages.chat import render_chat_page
from pages.debate import render_debate_page

# Set page configurations
st.set_page_config(
    page_title="LexFusion — Law RAG Workflow Automation",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_custom_css():
    """Loads and injects the premium static CSS stylesheet."""
    css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    # Load custom courtroom dark/gold theme stylesheet
    load_custom_css()

    # Initialize the API / Local fallback client
    if "api_client" not in st.session_state:
        st.session_state.api_client = LexFusionAPIClient()
    client = st.session_state.api_client

    # Sidebar Navigation and Branding
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 class="court-title" style="font-size: 1.8rem; margin: 0; color: #c9a84c;">
                🏛️ LEXFUSION
            </h2>
            <span style="font-size: 0.75rem; letter-spacing: 2px; color: #9ca3af; text-transform: uppercase;">
                Legal RAG Chamber
            </span>
        </div>
        <hr style="border-color: rgba(255,255,255,0.08); margin-top: 5px; margin-bottom: 20px;" />
        """,
        unsafe_allow_html=True,
    )

    # Ingestion Sector
    st.sidebar.markdown("### 📥 Ingest Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload Legal PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload contracts, court rulings, or case briefs for analysis.",
    )

    if uploaded_files:
        for file in uploaded_files:
            if f"uploaded_{file.name}" not in st.session_state:
                with st.sidebar.spinner(f"Ingesting {file.name}..."):
                    # Process document upload through API / Local mock
                    res = client.upload_document(file.name, file.read())
                    if res.get("status") == "success":
                        st.sidebar.success(f"Ingested: {file.name}")
                        st.session_state[f"uploaded_{file.name}"] = True
                    else:
                        st.sidebar.error(f"Failed: {file.name}")

    # Audio & Interactive FX Settings
    st.sidebar.markdown("### 🔊 Ambient Effects")
    st.session_state.sound_fx = st.sidebar.checkbox(
        "Enable Gavel Sound FX",
        value=True,
        help="Plays a realistic gavel strike sound effect when verdicts are rendered.",
    )

    # Display Collection Stats
    st.sidebar.markdown(
        """
        <div class="glass-card" style="margin-top: 15px; padding: 12px; background: rgba(255,255,255,0.02);">
            <div style="font-size: 0.78rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px;">Vector Database Stats</div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.9rem;">
                <span>📚 Collection Status:</span>
                <span class="gold-text" style="font-weight: 600;">ACTIVE</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                <span>📄 Loaded Documents:</span>
                <span style="font-weight: 600;">14</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation Tabs
    st.sidebar.markdown("### 🧭 Navigation")
    app_mode = st.sidebar.radio(
        "Select Chamber Interface",
        ["💬 Chat Assistant", "⚖️ Cross-Examine Debate"],
        label_visibility="collapsed",
    )

    # Network Status Badge
    mode_label = "LOCAL OFFLINE MODE" if client.local_mode else "API CONNECTED"
    mode_class = "badge-prosecution" if client.local_mode else "badge-defence"
    st.sidebar.markdown(
        f"""
        <div style="position: fixed; bottom: 20px; left: 20px; width: 260px;">
            <div style="text-align: center;">
                <span class="status-badge {mode_class}" style="font-size: 0.7rem; width: 100%;">
                    🔴 {mode_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Pages based on Navigation selection
    if app_mode == "💬 Chat Assistant":
        render_chat_page(client)
    else:
        render_debate_page(client)


if __name__ == "__main__":
    main()
