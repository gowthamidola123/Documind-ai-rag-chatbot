import streamlit as st
import os

from utils.pdf_loader import load_pdf
from utils.vector_store import create_vector_store
from utils.qa_chain import get_answer

st.set_page_config(page_title="DocuMind AI", layout="wide")

st.title("📚 DocuMind AI – Intelligent Document Assistant")

# ---------------- SESSION STATE ----------------
if "db" not in st.session_state:
    st.session_state.db = None

if "history" not in st.session_state:
    st.session_state.history = []

if "logs" not in st.session_state:
    st.session_state.logs = []

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "threshold" not in st.session_state:
    st.session_state.threshold = 0.5

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Upload Documents")

api_key = st.sidebar.text_input("OpenAI API Key", type="password")
pdf_files = st.sidebar.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

# ---------------- ADMIN LOGIN ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔐 Admin Login")

admin_pass = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_pass == "admin123":
    st.session_state.is_admin = True

# ---------------- PROCESS PDF ----------------
if pdf_files:
    all_text = ""

    with st.spinner("Processing documents..."):
        for file in pdf_files:
            all_text += load_pdf(file)

        st.session_state.db = create_vector_store(all_text)

    st.success("✅ Documents processed successfully!")

# ---------------- USER QUERY ----------------
query = st.text_input("💬 Ask a question")

if query and st.session_state.db:
    with st.spinner("Thinking..."):
        # ✅ UPDATED FUNCTION CALL (IMPORTANT)
        answer, docs = get_answer(
            st.session_state.db,
            query,
            api_key  # passing API key
        )

        # Save chat history
        st.session_state.history.append(("You", query))
        st.session_state.history.append(("AI", answer))

        # Save logs
        st.session_state.logs.append({
            "question": query,
            "answer": answer
        })

        st.session_state.query_count += 1

# ---------------- DISPLAY CHAT ----------------
st.markdown("## 💬 Chat")

for role, msg in st.session_state.history:
    if role == "You":
        st.markdown(f"**🧑 {msg}**")
    else:
        st.markdown(f"**🤖 {msg}**")

# ---------------- SOURCES ----------------
if query and st.session_state.db:
    docs = st.session_state.db.similarity_search(query)

    if docs:
        st.markdown("### 📌 Sources")
        for i, doc in enumerate(docs[:3]):
            st.write(f"Source {i+1}: {doc[:200]}...")

# ---------------- ADMIN DASHBOARD ----------------
if st.session_state.is_admin:
    st.markdown("---")
    st.header("🛠️ Admin Dashboard")

    col1, col2 = st.columns(2)
    col1.metric("Total Queries", st.session_state.query_count)
    col2.metric("Documents Loaded", "Yes" if st.session_state.db else "No")

    # Threshold control
    st.subheader("⚙️ Settings")
    st.session_state.threshold = st.slider(
        "Similarity Threshold",
        0.0, 1.0,
        st.session_state.threshold
    )

    # Logs
    st.subheader("📜 Recent Logs")
    for log in reversed(st.session_state.logs[-10:]):
        st.write("Q:", log["question"])
        st.write("A:", log["answer"])
        st.write("---")

    # Reset database
    if st.button("🗑️ Clear Database"):
        st.session_state.db = None
        st.success("Database cleared!")