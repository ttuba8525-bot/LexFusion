import streamlit as st
from typing import Dict, Any

def render_answer_card(answer: str, confidence: str, citation: Dict[str, Any], doc_name: str = None) -> None:
    """
    Renders a premium cited answer card in HTML/CSS.
    
    Args:
        answer: The text of the RAG model's answer.
        confidence: Confidence level ("High", "Medium", "Low").
        citation: Dictionary containing 'clause', 'page', and 'text'.
        doc_name: Optional name of the document.
    """
    confidence_lower = str(confidence).lower()
    badge_class = f"lex-badge-{confidence_lower}"
    
    doc_info_str = f'<span style="color: var(--text-secondary); font-size: 0.85rem;">📄 {doc_name}</span>' if doc_name else ''
    
    citation_html = ""
    if citation and isinstance(citation, dict):
        clause = citation.get("clause", "Relevant Provision")
        page = citation.get("page", "N/A")
        text = citation.get("text", "")
        
        citation_html = f"""
        <details class="lex-citation-details" style="margin-top: 15px; cursor: pointer; outline: none;">
            <summary style="color: var(--accent-gold); font-size: 0.9rem; font-weight: 600; font-family: 'Playfair Display', serif; display: flex; justify-content: space-between; align-items: center; list-style: none; user-select: none;">
                <span>🔍 Source: {clause} (Page {page})</span>
                <span style="font-size: 0.75rem; color: var(--text-secondary); border: 1px solid var(--border-color); padding: 2px 6px; border-radius: 4px;">Toggle Text</span>
            </summary>
            <div class="lex-citation-box" style="margin-top: 8px;">
                <div class="lex-citation-text" style="color: #D1D5DB; font-size: 0.9rem; line-height: 1.5;">{text}</div>
            </div>
        </details>
        """
        
    card_html = f"""
    <div class="lex-answer-card">
        <div class="lex-answer-header">
            <span class="lex-badge {badge_class}">{confidence} Confidence</span>
            {doc_info_str}
        </div>
        <div class="lex-answer-body">{answer}</div>
        {citation_html}
    </div>
    """
    
    # Clean newlines and collapse multiple spaces to prevent Streamlit's markdown parser
    # from incorrectly rendering indented HTML blocks as markdown code blocks.
    import re
    cleaned_html = re.sub(r'\s+', ' ', card_html).strip()
    st.markdown(cleaned_html, unsafe_allow_html=True)
