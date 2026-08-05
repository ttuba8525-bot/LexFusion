"""
LexFusion PDF & Legal Brief Exporter
=====================================
Generates printable, formatted Legal Brief HTML/PDF reports
complete with cover branding, debate summaries, and cited evidence.
"""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Any


def generate_legal_brief_html(query: str, debate_data: dict[str, Any]) -> str:
    """
    Generates a beautifully styled HTML court brief document suitable
    for browser printing or saving directly as a PDF.
    """
    timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    history = debate_data.get("argument_history", [])
    synthesis = debate_data.get("synthesis", "No synthesis provided.")
    confidence = debate_data.get("confidence_score", 50)
    sources = debate_data.get("source_documents", [])

    rounds_html = ""
    for entry in history:
        adv = entry.get("advocate", "A")
        role = entry.get("role", "Counsel")
        arg = entry.get("argument", "")
        r_num = entry.get("round", 1)

        border_color = "#c9a84c" if adv == "A" else "#3b82f6"
        badge_bg = "#fef3c7" if adv == "A" else "#dbeafe"
        badge_fg = "#b45309" if adv == "A" else "#1e40af"

        rounds_html += f"""
        <div style="margin-bottom: 20px; border-left: 4px solid {border_color}; padding-left: 15px;">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: #6b7280;">
                ROUND {r_num} • <span style="background: {badge_bg}; color: {badge_fg}; padding: 2px 8px; border-radius: 4px; font-weight: bold;">{role} (ADVOCATE {adv})</span>
            </div>
            <p style="margin-top: 8px; font-size: 0.95rem; line-height: 1.6; color: #1f2937;">
                {arg}
            </p>
        </div>
        """

    sources_html = ""
    for idx, doc in enumerate(sources):
        src = doc.get("source", "Document")
        pg = doc.get("page", "?")
        txt = doc.get("chunk", "")
        sources_html += f"""
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
            <div style="font-weight: bold; font-size: 0.85rem; color: #374151;">
                Exhibit #{idx+1}: {src} (Page {pg})
            </div>
            <p style="font-style: italic; font-size: 0.88rem; color: #4b5563; margin-top: 4px; margin-bottom: 0;">
                "{txt}"
            </p>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>LexFusion — Official Legal Brief</title>
        <style>
            @body {{ font-family: 'Georgia', serif; color: #111827; padding: 40px; max-width: 800px; margin: 0 auto; }}
            h1 {{ font-family: 'Times New Roman', serif; text-transform: uppercase; border-bottom: 2px solid #111827; padding-bottom: 10px; margin-bottom: 5px; }}
            .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; margin-top: 20px; }}
            .header-table td {{ padding: 6px; font-size: 0.9rem; border-bottom: 1px solid #e5e7eb; }}
            .section-title {{ font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #1e3a8a; border-bottom: 1px solid #93c5fd; padding-bottom: 4px; margin-top: 30px; margin-bottom: 15px; }}
            .verdict-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 8px; margin-bottom: 25px; }}
            @media print {{ body {{ padding: 0; }} .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 1.8rem; font-weight: bold; font-family: 'Times New Roman', serif;">OFFICIAL COURT BRIEF & LEGAL ANALYSIS</div>
            <div style="font-size: 0.9rem; letter-spacing: 2px; color: #6b7280; text-transform: uppercase; margin-top: 5px;">LexFusion Autonomous RAG System</div>
        </div>

        <table class="header-table">
            <tr>
                <td><strong>CASE MATTER / ISSUE:</strong></td>
                <td>{query}</td>
            </tr>
            <tr>
                <td><strong>DATE OF EXAMINATION:</strong></td>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <td><strong>VERDICT CERTAINTY SCORE:</strong></td>
                <td><strong>{confidence}%</strong></td>
            </tr>
        </table>

        <div class="section-title">I. Presiding Judicial Synthesis & Ruling</div>
        <div class="verdict-box">
            <p style="font-size: 1rem; line-height: 1.7; color: #14532d; margin: 0;">
                {synthesis}
            </p>
        </div>

        <div class="section-title">II. Adversarial Debate Transcript</div>
        {rounds_html}

        <div class="section-title">III. Cited Statutory Evidence Index</div>
        {sources_html}

        <hr style="margin-top: 40px; border: 0; border-top: 1px dashed #9ca3af;" />
        <div style="text-align: center; font-size: 0.75rem; color: #9ca3af; margin-top: 10px;">
            CONFIDENTIAL & PROPRIETARY — GENERATED BY LEXFUSION MULTI-AGENT ENGINE
        </div>
    </body>
    </html>
    """
    return html_content
