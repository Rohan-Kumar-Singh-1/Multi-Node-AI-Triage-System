# 🤖 Multi-Node AI Triage System

A **production-style AI application** built using **LangGraph + Streamlit + OpenRouter**, featuring multi-node routing, session-based conversations, authentication, and persistent memory.

---

## 🚀 Features

### 🧠 AI Capabilities

* LLM-based **intent classification** (Billing, Technical Support, General)
* **Multi-node architecture** using LangGraph
* **Tool-augmented responses** (Tech Support node)
* **Context-aware memory** (LLM sees previous messages)

### 💬 Chat System

* Multi-session chat (like ChatGPT)
* Persistent conversation history (SQLite)
* Sidebar session switching
* New chat creation

### 🔐 Authentication

* User login/signup system
* Session-based user isolation

### 🖥️ UI

* Built with Streamlit
* Chat-style interface
* Sidebar navigation

---

## 🏗️ Architecture

User Query → Router Node → (Billing | Tech Support | General) → Response
                                                    ↓
                                                SQLite (Users + Chat History)

---

## 🧩 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **AI Framework**: LangGraph, LangChain
* **LLM Provider**: OpenRouter
* **Database**: SQLite

---

## 📂 Project Structure

```
.
├── app.py
├── requirements.txt
├── .env
├── app.db
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-triage-system.git
cd ai-triage-system
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Add Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

---

### 4. Run the App

```bash
streamlit run app.py
```

---

## 🧠 How It Works

### 1. Routing

* A router node uses an LLM to classify queries into:

  * Billing
  * Technical Support
  * General

### 2. Conditional Flow

* Based on classification, queries are routed using **LangGraph conditional edges**

### 3. Tool Usage

* Tech Support node uses a **dummy troubleshooting tool**

### 4. Memory System

* Previous messages are fetched from the database
* Injected into the LLM prompt for context-aware responses

### 5. Session Management

* Each chat session is assigned a unique UUID
* Conversations are grouped and persisted

---

## 🔐 Security Note

* Passwords are currently stored in plain text (for demo purposes)
* For production, use:

  * bcrypt hashing
  * secure authentication flows

---

## 📸 Demo Features

* Login / Signup
* Multi-session chat
* Sidebar chat navigation
* Context-aware AI responses

---

## 🚀 Future Improvements

* 🔐 Password hashing (bcrypt)
* 🏷️ Rename chat sessions
* 🔍 Search conversations
* 🧠 Advanced memory (summarization / embeddings)
* ☁️ Deployment (Streamlit Cloud / Render)

---

## 🎯 Key Learnings

* State management using LangGraph
* LLM-based routing systems
* Building persistent AI applications
* Session-based architecture design
* Integrating tools with LLM workflows

---

## 🧠 Interview Summary

> Built a stateful, multi-node AI system with LLM-based routing, tool integration, session-based memory, and persistent storage, wrapped in an interactive Streamlit interface.

---

## 📜 License

This project is for educational and demonstration purposes.
