import streamlit as st
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import sqlite3
import uuid

load_dotenv()

# ---------------------------
# DATABASE SETUP
# ---------------------------
conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    session_id TEXT,
    query TEXT,
    response TEXT
)
""")

conn.commit()

# ---------------------------
# AUTH FUNCTIONS
# ---------------------------
def create_user(username, password):
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cursor.fetchone()

def save_chat(username, session_id, query, response):
    cursor.execute(
        "INSERT INTO history (username, session_id, query, response) VALUES (?, ?, ?, ?)",
        (username, session_id, query, response)
    )
    conn.commit()

def load_sessions(username):
    cursor.execute(
        "SELECT DISTINCT session_id FROM history WHERE username=? ORDER BY id DESC",
        (username,)
    )
    return cursor.fetchall()

def load_session_chats(session_id):
    cursor.execute(
        "SELECT query, response FROM history WHERE session_id=?",
        (session_id,)
    )
    return cursor.fetchall()

# ---------------------------
# 🧠 MEMORY CONTEXT BUILDER
# ---------------------------
def build_context(session_id, current_query):
    chats = load_session_chats(session_id)

    context = ""
    for q, r in chats[-5:]:  # last 5 interactions
        context += f"User: {q}\nAssistant: {r}\n"

    context += f"User: {current_query}\n"
    return context

# ---------------------------
# LLM SETUP
# ---------------------------
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

# ---------------------------
# STATE
# ---------------------------
class AgentState(TypedDict):
    query: str
    category: str
    response: str

# ---------------------------
# ROUTER NODE
# ---------------------------
def router_node(state: AgentState):
    prompt = f"""
    Classify into:
    - Billing
    - Technical Support
    - General

    Query: {state['query']}

    Only return category.
    """
    category = llm.invoke(prompt).content.strip()
    return {"category": category}

# ---------------------------
# TOOL
# ---------------------------
def troubleshoot_tool(issue: str) -> str:
    return """
    1. Restart system
    2. Check internet
    3. Update software
    4. Contact support
    """

# ---------------------------
# NODES (WITH MEMORY)
# ---------------------------
def billing_node(state: AgentState):
    context = build_context(st.session_state.chat_session_id, state["query"])

    response = llm.invoke(f"""
    You are a billing assistant.

    Conversation:
    {context}

    Answer the latest query properly.
    """).content

    return {"response": response}

def tech_support_node(state: AgentState):
    context = build_context(st.session_state.chat_session_id, state["query"])
    steps = troubleshoot_tool(state["query"])

    response = llm.invoke(f"""
    You are a technical support assistant.

    Troubleshooting steps:
    {steps}

    Conversation:
    {context}

    Answer clearly and progressively.
    """).content

    return {"response": response}

def general_node(state: AgentState):
    context = build_context(st.session_state.chat_session_id, state["query"])

    response = llm.invoke(f"""
    Conversation:
    {context}

    Respond naturally and contextually.
    """).content

    return {"response": response}

# ---------------------------
# ROUTING
# ---------------------------
def route_decision(state: AgentState):
    cat = state["category"].lower()

    if "billing" in cat:
        return "billing"
    elif "technical" in cat:
        return "tech_support"
    else:
        return "general"

# ---------------------------
# GRAPH
# ---------------------------
builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("billing", billing_node)
builder.add_node("tech_support", tech_support_node)
builder.add_node("general", general_node)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "billing": "billing",
        "tech_support": "tech_support",
        "general": "general"
    }
)

builder.add_edge("billing", END)
builder.add_edge("tech_support", END)
builder.add_edge("general", END)

graph = builder.compile()

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="AI Triage System", layout="wide")

# SESSION STATE
if "user" not in st.session_state:
    st.session_state.user = None

if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())

# ---------------------------
# LOGIN / SIGNUP
# ---------------------------
if st.session_state.user is None:
    st.title("🔐 Login / Signup")

    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Signup":
        if st.button("Create Account"):
            if create_user(username, password):
                st.success("Account created!")
            else:
                st.error("User already exists")

    if menu == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ---------------------------
# MAIN APP
# ---------------------------
st.title("🤖 AI Triage System")

st.sidebar.write(f"👤 {st.session_state.user}")

# LOGOUT
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ---------------------------
# ➕ NEW CHAT
# ---------------------------
if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.rerun()

# ---------------------------
# SIDEBAR SESSIONS
# ---------------------------
st.sidebar.subheader("🕘 Chat Sessions")

sessions = load_sessions(st.session_state.user)

for (session_id,) in sessions:
    if st.sidebar.button(session_id[:8], key=session_id):
        st.session_state.chat_session_id = session_id
        st.rerun()

# ---------------------------
# DISPLAY CURRENT SESSION
# ---------------------------
chats = load_session_chats(st.session_state.chat_session_id)

for q, r in chats:
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(r)

# ---------------------------
# INPUT
# ---------------------------
user_query = st.chat_input("Ask something...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    with st.spinner("Thinking..."):
        result = graph.invoke({
            "query": user_query,
            "category": "",
            "response": ""
        })

    final_response = f"[{result['category']}] {result['response']}"

    with st.chat_message("assistant"):
        st.write(final_response)

    save_chat(
        st.session_state.user,
        st.session_state.chat_session_id,
        user_query,
        final_response
    )