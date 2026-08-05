import streamlit as st
import re
from typing import Dict, Any

def render_advocate_card(side: str, title: str, argument_text: str) -> None:
    """
    Renders an Advocate Column card (Advocate A or Advocate B) with custom styles.
    
    Args:
        side: 'A' or 'B' (determines border colors, backgrounds, and icons).
        title: Title of the advocate and party they represent.
        argument_text: Content of the argument (basic markdown format).
    """
    icon = "🛡️" if side.upper() == 'A' else "⚔️"
    side_lower = side.lower()
    card_class = f"advocate-card advocate-card-{side_lower}"
    icon_class = f"advocate-icon advocate-icon-{side_lower}"
    
    # Process basic markdown to HTML elements for proper styling inside the custom container
    html_content = argument_text
    # 1. Headers
    html_content = re.sub(r'### (.*)', r'<h4 style="margin-top:0; font-family:\'Playfair Display\', serif; font-size:1.15rem; color:var(--text-primary);">\1</h4>', html_content)
    # 2. Bold
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    # 3. Lists
    lines = html_content.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* '):
            item_text = stripped[2:]
            if not in_list:
                new_lines.append('<ul style="margin: 8px 0; padding-left: 20px; color: #D1D5DB;">')
                in_list = True
            new_lines.append(f'<li style="margin-bottom: 8px;">{item_text}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append('</ul>')
    html_content = '\n'.join(new_lines)
    
    # Replace single line breaks with <br> where they are not in list blocks
    html_content = html_content.replace('\n', '<br>')
    
    html = f"""
    <div class="{card_class}">
        <div class="advocate-header">
            <span class="{icon_class}">{icon}</span>
            <h3 class="advocate-title">{title}</h3>
        </div>
        <div class="advocate-content">
            {html_content}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_judge_verdict_card(verdict: Dict[str, Any]) -> None:
    """
    Renders the judge's synthesized verdict card with high-end legal styling.
    
    Args:
        verdict: Dict containing 'ruling', 'supported_side', 'neutral_meaning',
                 'rationale', and 'citation'.
    """
    if not verdict:
        return
        
    ruling = verdict.get("ruling", "No ruling rendered.")
    supported_side = verdict.get("supported_side", "Tie")
    neutral_meaning = verdict.get("neutral_meaning", "N/A")
    rationale = verdict.get("rationale", "")
    citation = verdict.get("citation")
    
    citation_html = ""
    if citation and isinstance(citation, dict):
        clause = citation.get("clause", "Relevant Clause")
        page = citation.get("page", "N/A")
        text = citation.get("text", "")
        citation_html = f"""
        <div class="lex-citation-box" style="margin-top: 20px; border-left-color: var(--accent-gold); background-color: rgba(0,0,0,0.3);">
            <div class="lex-citation-title" style="color: var(--accent-gold); display: flex; justify-content: space-between; font-weight: 600;">
                <span>⚖️ Verdict Citation: {clause}</span>
                <span>Page {page}</span>
            </div>
            <div class="lex-citation-text" style="color: #D1D5DB; margin-top: 8px; font-style: italic;">{text}</div>
        </div>
        """
        
    html = f"""
    <div class="judge-ruling-card">
        <div class="judge-ruling-header">
            <span style="font-size: 1.8rem; color: var(--accent-gold);">⚖️</span>
            <h2 class="judge-ruling-title legal-serif" style="margin: 0; font-size: 1.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Synthesized Ruling</h2>
        </div>
        
        <div class="judge-meta-row">
            <div class="judge-meta-item">
                <span class="judge-meta-label">Supported Party</span>
                <span class="judge-meta-value" style="color: var(--accent-gold); font-size: 1rem; font-weight: 700;">{supported_side}</span>
            </div>
            <div class="judge-meta-item" style="flex: 1; min-width: 250px;">
                <span class="judge-meta-label">Neutral Meaning</span>
                <span class="judge-meta-value" style="font-weight: 400; color: #E5E7EB; font-size: 0.95rem; line-height: 1.4;">{neutral_meaning}</span>
            </div>
        </div>
        
        <div class="judge-verdict-section">
            <div class="judge-verdict-title legal-serif">The Court's Final Finding</div>
            <div class="judge-verdict-text legal-serif">{ruling}</div>
        </div>
        
        <div style="font-size: 0.95rem; line-height: 1.6; color: #D1D5DB; margin-top: 15px;">
            <strong style="color: var(--accent-gold);">Judicial Rationale:</strong> {rationale}
        </div>
        
        {citation_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
