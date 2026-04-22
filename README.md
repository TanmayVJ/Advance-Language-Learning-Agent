# 🌍 Advance Language Learning Agent

> A conversational AI tutor that helps you practice real languages through natural dialogue — with mistake tracking, vocabulary lessons, and grammar drills built in.

Developed by **Tanmay Vijayvargiya**  
📧 tanmayvijayvargiya.work@gmail.com  
🔗 [linkedin.com/in/tanmay-vijayvargiya](https://www.linkedin.com/in/tanmay-vijayvargiya)

---

## 📸 Preview

```
💬 You:   Bonjour! Je veux commander un café.
🤖 Léa:  Bonjour! Bien sûr, quelle taille vous voulez?
          ---
          📝 Quick correction: "Je veux" → "Je voudrais" 
          💡 Why: "Je voudrais" is more polite when ordering in French.
          ---
```

---

## ✨ Features

- **12 Languages** — Spanish, French, German, Japanese, Italian, Portuguese, Korean, Mandarin, Hindi, Arabic, Russian, Turkish
- **3 Proficiency Levels** — Beginner, Intermediate, Advanced
- **Dynamic Scenes** — Randomised real-world practice scenarios (café, job interview, travel, etc.)
- **Smart Mistake Tracking** — Corrections are detected, explained, and saved to a local database
- **Vocabulary Builder** — Generate a focused lesson on any topic on demand
- **Grammar Drills** — Fill-in-blank and translation exercises for any grammar point
- **Mistake Log Tab** — Review all past corrections with explanations
- **Chat Export** — Download your full conversation as a `.txt` file
- **Session Memory** — Conversation history maintained across messages within a session

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web UI |
| [LangChain](https://langchain.com) | LLM abstraction layer |
| [Groq API](https://console.groq.com) | Free, fast AI inference |
| LLaMA 3.3 70B | Language model (via Groq) |
| SQLite | Local mistake & session storage |
| Python 3.9+ | Core language |

---

## 🚀 Getting Started

### 1. Get a Free Groq API Key
- Go to [console.groq.com](https://console.groq.com)
- Sign up (free, no credit card needed)
- Click **API Keys → Create API Key**
- Copy the key — it starts with `gsk_...`

### 2. Clone or Download This Project
```bash
git clone https://github.com/your-username/language-learning-chatbot.git
cd language-learning-chatbot
```
Or just download the ZIP and extract it.

### 3. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
streamlit run language_learning_chatbot.py
```

Open your browser at **http://localhost:8501**

---

## 🎮 How to Use

1. Paste your Groq API key in the sidebar
2. Select the language you want to learn
3. Choose your native language and proficiency level
4. Click **🚀 Start Session**
5. Start chatting — your AI tutor Léa will guide, correct, and encourage you

### Tabs Available
| Tab | Description |
|---|---|
| 💬 Conversation | Main chat with the AI tutor |
| 🛠️ Practice Tools | Vocabulary lessons & grammar drills |
| 📋 Mistake Log | Review all corrections from your sessions |

---

## 📁 Project Structure

```
language-learning-chatbot/
│
├── language_learning_chatbot.py   # Main application file
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── language_learning.db           # Auto-created on first run (SQLite)
```

---

## 🔧 Configuration

### Switching the AI Model
In `language_learning_chatbot.py`, find the `build_llm()` function and change `model_name`:

```python
# Current (recommended — best quality, free)
model_name="llama-3.3-70b-versatile"

# Faster, lighter option
model_name="llama-3.1-8b-instant"

# Google's Gemma 2 (great multilingual support)
model_name="gemma2-9b-it"

# Mixtral (strong at multilingual tasks)
model_name="mixtral-8x7b-32768"
```

### Using OpenAI Instead
Replace the `build_llm()` function with:
```python
from langchain_openai import ChatOpenAI

def build_llm(api_key):
    return ChatOpenAI(openai_api_key=api_key, model_name="gpt-4o", temperature=0.7)
```
Everything else stays the same — that's the benefit of the LangChain abstraction.

---

## 🐛 Common Issues

**`sqlite3.OperationalError: no such column: session_date`**  
→ An old database file exists from a previous version. Find and delete `language_learning.db`, then rerun the app. It will create a fresh one automatically.

**`ModuleNotFoundError: No module named 'langchain_groq'`**  
→ Your virtual environment may not be activated. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux), then `pip install -r requirements.txt` again.

**API Error in chat**  
→ Check your Groq API key is pasted correctly with no extra spaces. It should start with `gsk_`.

**Port already in use**  
→ Run `streamlit run language_learning_chatbot.py --server.port 8502`

---

## 🔮 Roadmap / Future Improvements

- [ ] User authentication for persistent profiles across devices
- [ ] Streaming responses for faster feel
- [ ] Speech-to-text input using Whisper
- [ ] Pronunciation feedback
- [ ] Spaced repetition system for vocabulary review
- [ ] PostgreSQL support for multi-user deployment
- [ ] Deploy to Streamlit Cloud / Hugging Face Spaces

---


## 🙏 Acknowledgements

- [Groq](https://groq.com) for the incredibly fast and free LLM inference
- [LangChain](https://langchain.com) for the clean LLM abstraction layer
- [Streamlit](https://streamlit.io) for making AI apps easy to build and share
- Meta AI for the open-source LLaMA 3.3 model
