import streamlit as st
import time
from frontend.components.answer_card import render_answer_card
from frontend.utils import api_client

# 1. Page Header (Page specific title)
st.markdown('<h1 class="legal-serif" style="font-size: 2.2rem; margin-top: 10px; margin-bottom: 5px;">Document Q&A Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: var(--text-secondary); margin-bottom: 25px;">Ask questions in plain English and retrieve answers grounded in contract clauses with full citation support.</p>', unsafe_allow_html=True)

# 2. Sidebar Document Management Panel
st.sidebar.markdown('<h3 class="legal-serif" style="color: var(--accent-gold); margin-top: 15px;">Document Ingestion</h3>', unsafe_allow_html=True)

# Handle file upload or demo loading
uploaded_file = st.sidebar.file_uploader(
    "Upload legal contract (PDF)", 
    type=["pdf"],
    help="Upload a PDF file to run queries against its contents."
)

# Check if user clicked "Clear Document"
clear_doc = st.sidebar.button("Clear Active Document", key="clear_doc_btn", type="secondary")
if clear_doc:
    st.session_state.uploaded_doc = None
    st.session_state.chat_history = []
    st.rerun()

# Simulate ingestion flow for newly uploaded file
if uploaded_file is not None:
    # Only run if it's a new file
    current_doc = st.session_state.uploaded_doc
    if current_doc is None or current_doc.get("filename") != uploaded_file.name:
        with st.sidebar.status("Ingesting PDF document...", expanded=True) as status:
            st.write("Reading raw PDF text...")
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            st.write("Chunking and identifying contract clauses...")
            time.sleep(0.6)
            st.write("Generating embeddings and building vector index...")
            time.sleep(0.6)
            
            # Call API Client
            doc_info = api_client.upload_document(uploaded_file.name, uploaded_file.read())
            status.update(label="Document indexed successfully!", state="complete", expanded=False)
            
        st.session_state.uploaded_doc = doc_info
        st.session_state.chat_history = []  # Clear history for new document
        st.rerun()

# If no file uploaded but demo isn't loaded either, let them load a demo
if st.session_state.uploaded_doc is None:
    st.sidebar.info("No active document loaded. Upload a PDF or click 'Load Demo Contract' on the right to start.")

# Document details display
if st.session_state.uploaded_doc:
    doc = st.session_state.uploaded_doc
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(196, 151, 70, 0.05); border: 1px solid var(--accent-gold); padding: 12px; border-radius: 6px; margin-top: 15px;">
            <div style="color: var(--accent-gold); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 8px;">Active Index Status</div>
            <div style="font-size: 0.9rem; margin-bottom: 4px;"><strong>File:</strong> {doc.get('filename')}</div>
            <div style="font-size: 0.9rem; margin-bottom: 4px;"><strong>Pages:</strong> {doc.get('pages')}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);"><strong>Loaded:</strong> {doc.get('uploaded_at')[:10]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 3. Main Chat Layout
suggested_questions = [
    "Is there a change of control clause, and what are the triggers?",
    "What is the limit of liability under the contract?",
    "What happens if a party defaults or fails to perform?",
    "Are there any intellectual property indemnification exclusions?"
]

def load_demo_and_execute_question(question: str):
    """Loads the demo merger agreement and inserts the selected question."""
    st.session_state.uploaded_doc = api_client.MOCK_DOCUMENTS["doc_merger_2026"]
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # Show spinner and query API
    with st.spinner("LexFusion is retrieving clauses and formulating answer..."):
        response = api_client.ask_question(question, "doc_merger_2026")
        
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response.get("answer", ""),
        "confidence": response.get("confidence", "Medium"),
        "citation": response.get("citation", {})
    })
    st.rerun()

# Render empty state if no document is active
if st.session_state.uploaded_doc is None:
    st.markdown(
        """
        <div class="lex-empty-state">
            <div class="lex-empty-icon">⚖️</div>
            <h2 class="legal-serif" style="font-size: 1.6rem; color: var(--accent-gold); margin-bottom: 8px;">LexFusion Legal RAG Engine</h2>
            <p style="color: var(--text-secondary); max-width: 600px; margin: 0 auto 20px auto; font-size: 0.95rem; line-height: 1.6;">
                Welcome to LexFusion. To start Q&A, upload a PDF contract in the sidebar or load our pre-indexed merger agreement demo.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Load demo button in empty state
    col_demo, _ = st.columns([1, 2])
    with col_demo:
        if st.button("🚀 Load Demo Merger Agreement", key="load_demo_btn", type="primary"):
            st.session_state.uploaded_doc = api_client.MOCK_DOCUMENTS["doc_merger_2026"]
            st.session_state.chat_history = []
            st.rerun()
            
    st.markdown('<div class="lex-suggested-title">Or ask a quick demo question (Autoloads Contract):</div>', unsafe_allow_html=True)
    for i, q in enumerate(suggested_questions):
        if st.button(q, key=f"sugg_empty_{i}", help="Click to load document and execute query"):
            load_demo_and_execute_question(q)

else:
    # Document is active: display chat history
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            # Styled User chat message
            st.chat_message("user").write(msg["content"])
        else:
            # Assistant message using the reusable cited-answer card
            with st.chat_message("assistant"):
                render_answer_card(
                    answer=msg["content"],
                    confidence=msg.get("confidence", "High"),
                    citation=msg.get("citation", {}),
                    doc_name=st.session_state.uploaded_doc.get("filename")
                )
                
    # Suggested Questions sidebar accordion or quick panel
    with st.expander("💡 Suggested Questions", expanded=False):
        for i, q in enumerate(suggested_questions):
            if st.button(q, key=f"sugg_active_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("LexFusion is reviewing contract details..."):
                    response = api_client.ask_question(q, st.session_state.uploaded_doc["doc_id"])
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.get("answer", ""),
                    "confidence": response.get("confidence", "Medium"),
                    "citation": response.get("citation", {})
                })
                st.rerun()

    # Chat input box
    user_query = st.chat_input("Ask a question about the clauses in this contract...")
    if user_query:
        # 1. Display user query immediately
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.rerun()

# Trigger response generation if the last message is from user
if st.session_state.uploaded_doc and st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    last_query = st.session_state.chat_history[-1]["content"]
    
    # Render user message
    # Wait, we need to show the spinner/thinking state
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            """
            <div style="display: flex; gap: 8px; align-items: center; padding: 10px; color: var(--text-secondary);">
                <span class="spinner" style="width: 10px; height: 10px; border-radius: 50%; background: var(--accent-gold); display: inline-block; animation: blink 1.4s infinite both;"></span>
                <span style="font-family: 'Playfair Display', serif; font-style: italic;">LexFusion is interpreting clauses...</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Query API Client
        response = api_client.ask_question(last_query, st.session_state.uploaded_doc["doc_id"])
        thinking_placeholder.empty()
        
        # Save response in state
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.get("answer", ""),
            "confidence": response.get("confidence", "Medium"),
            "citation": response.get("citation", {})
        })
        st.rerun()
