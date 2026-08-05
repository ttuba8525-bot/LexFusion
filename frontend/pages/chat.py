"""
LexFusion Single-Shot RAG Assistant Page
=========================================
Simple, clean conversational chat interface for asking direct
legal questions about the uploaded document corpus.
"""

from __future__ import annotations

import streamlit as st
from utils.api_client import LexFusionAPIClient
from components.answer_card import render_source_cards


def render_chat_page(client: LexFusionAPIClient):
    """Renders the single-shot RAG Chat assistant."""
    st.markdown(
        """
        <div class="title-banner">
            <h1 class="court-title" style="font-size: 2.4rem; margin-bottom: 8px;">
                ⚖️ LEXFUSION <span class="gold-text">RESEARCH ASSISTANT</span>
            </h1>
            <p style="color: #9ca3af; font-size: 0.98rem; margin: 0; letter-spacing: 0.5px;">
                Direct Legal Query Engine & Grounded Document Corpus Analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initalize message history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                render_source_cards(message["sources"])

    # User input
    if prompt := st.chat_input("Enter your legal question..."):
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call RAG API (non-debate mode)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document corpus..."):
                response = client.query(query=prompt, debate_mode=False)

            if "answer" in response:
                answer = response["answer"]
                sources = response.get("source_documents", [])

                st.markdown(answer)
                render_source_cards(sources)

                # Store assistant response
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )
            else:
                err_msg = response.get("error_message", "Inference failed.")
                st.error(f"Error analyzing query: {err_msg}")
