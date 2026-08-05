import streamlit as st
import os

# 1. Set Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="LexFusion Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization
if "uploaded_doc" not in st.session_state:
    st.session_state.uploaded_doc = None  # Dict of {doc_id, filename, title, pages, uploaded_at}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of {"role": "user" or "assistant", "content", "confidence", "citation"}
if "debate_history" not in st.session_state:
    st.session_state.debate_history = {}  # Cache of debate results to prevent unnecessary reruns: {question: debate_dict}
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# 3. Load and Inject Stylesheet
def inject_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
        # Append Light Theme variable overrides dynamically if selected
        if st.session_state.theme == "light":
            light_override = """
            :root {
                --bg-primary: #F3F5F8;
                --bg-secondary: #FFFFFF;
                --bg-card: #E4EBF3;
                --bg-image: none;
                --accent-gold: #96702D;
                --accent-gold-hover: #7E5C22;
                --accent-gold-glow: rgba(150, 112, 45, 0.12);
                --advocate-a: #2E65C0;
                --advocate-a-bg: rgba(46, 101, 192, 0.04);
                --advocate-b: #C96623;
                --advocate-b-bg: rgba(201, 102, 35, 0.04);
                --judge-border: #96702D;
                --judge-bg: rgba(150, 112, 45, 0.03);
                --text-primary: #1F2633;
                --text-secondary: #5F6B7E;
                --border-color: #D1D9E6;
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.05);
                --shadow-md: 0 8px 24px rgba(67, 85, 114, 0.08);
                --shadow-lg: 0 16px 40px rgba(67, 85, 114, 0.12);
                --glass-bg: rgba(255, 255, 255, 0.85);
                --glass-blur: blur(12px);
            }
            /* Input element overrides for light mode */
            div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {
                color: #1F2633 !important;
            }
            .stChatMessage {
                background-color: #FFFFFF !important;
                border: 1px solid #D1D9E6 !important;
            }
            .stChatMessage p {
                color: #1F2633 !important;
            }
            """
            css_content += "\n" + light_override
            
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# 4. Theme Selection (Rendered first so CSS updates on interaction)
# Render animated scales of justice
st.sidebar.markdown('<div class="animated-scale">⚖️</div>', unsafe_allow_html=True)

st.sidebar.markdown(
    '<h1 class="legal-title" style="font-size: 1.8rem; text-align: center; margin-bottom: 2px;">LEXFUSION</h1>', 
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<p style="text-align: center; color: var(--accent-gold); font-size: 0.8rem; margin-top: 0; margin-bottom: 15px; letter-spacing: 0.1em; font-family: \'Inter\', sans-serif;">ADVERSARIAL RAG</p>', 
    unsafe_allow_html=True
)

st.sidebar.markdown('<hr style="border-top: 1px solid var(--border-color); margin: 10px 0 20px 0;">', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: var(--text-secondary); font-size: 0.75rem; margin-bottom: 5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; text-align: center;">Interface Theme</p>', unsafe_allow_html=True)
is_light = st.sidebar.toggle("☀️ Light Mode Theme", value=(st.session_state.theme == "light"))
new_theme = "light" if is_light else "dark"
if new_theme != st.session_state.theme:
    st.session_state.theme = new_theme
    st.rerun()

# Apply CSS
inject_custom_css()

# 5. Global Branded Header
active_doc_name = "None"
if st.session_state.uploaded_doc:
    active_doc_name = st.session_state.uploaded_doc.get("filename", "Active Document")

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.8rem; line-height: 1;">⚖️</span>
            <span class="legal-serif" style="font-size: 1.4rem; font-weight: 700; color: var(--accent-gold); letter-spacing: 0.05em;">LEXFUSION</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); background: rgba(255, 255, 255, 0.02); padding: 5px 12px; border-radius: 4px; border: 1px solid var(--border-color); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--text-secondary);">ACTIVE DOC:</span>
            <strong style="color: var(--accent-gold); font-family: 'Playfair Display', serif; font-size: 0.9rem;">{active_doc_name}</strong>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# 6. Define Pages & Navigation
pages = [
    st.Page("pages/chat.py", title="Document Q&A", icon="💬"),
    st.Page("pages/debate.py", title="Adversarial Debate", icon="⚖️")
]

pg = st.navigation(pages)
pg.run()
