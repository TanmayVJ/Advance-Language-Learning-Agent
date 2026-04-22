# ============================================================
#              AI Language Learning Chatbot
#         Developed by Tanmay Vijayvargiya
#  tanmayvijayvargiya.work@gmail.com | linkedin.com/in/tanmay-vijayvargiya
# ============================================================

# WHY THIS ARCHITECTURE:
# - Groq API is used because it's FREE for development/testing and blazing fast
#   (supports llama-3.3-70b-versatile, gemma2-9b-it, mixtral, etc.)
# - SQLite keeps things portable — no external DB needed for a portfolio project
# - LangChain keeps the AI layer swappable; you can plug in OpenAI/Gemini later
# - Streamlit is chosen for rapid, clean UI without writing any HTML/CSS
# ============================================================

import os
import re
import random
import sqlite3
from datetime import datetime

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# ── Constants ─────────────────────────────────────────────────────────────────

LANGUAGES = {
    "🇪🇸 Spanish":    "Spanish",
    "🇫🇷 French":     "French",
    "🇩🇪 German":     "German",
    "🇯🇵 Japanese":   "Japanese",
    "🇮🇹 Italian":    "Italian",
    "🇵🇹 Portuguese": "Portuguese",
    "🇰🇷 Korean":     "Korean",
    "🇨🇳 Mandarin":   "Mandarin Chinese",
    "🇮🇳 Hindi":      "Hindi",
    "🇸🇦 Arabic":     "Arabic",
    "🇷🇺 Russian":    "Russian",
    "🇹🇷 Turkish":    "Turkish",
}

NATIVE_LANGUAGES = {
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English":    "English",
    "🇪🇸 Spanish":  "Spanish",
    "🇫🇷 French":   "French",
    "🇩🇪 German":   "German",
    "🇮🇳 Hindi":    "Hindi",
    "🇵🇹 Portuguese": "Portuguese",
}

LEVELS = ["🌱 Beginner", "⚡ Intermediate", "🚀 Advanced"]

SCENES = {
    "🌱 Beginner":      ["Ordering at a café ☕", "Introducing yourself 🤝", "Asking for directions 🗺️", "Shopping at a market 🛍️"],
    "⚡ Intermediate":  ["Discussing weekend plans 🎨", "Talking about your job 💼", "Describing a movie you watched 🎬", "Travel stories ✈️"],
    "🚀 Advanced":      ["Debating a social issue 🎤", "Explaining a complex idea 💡", "Business negotiation 📊", "Reviewing a book 📖"],
}

MOTIVATIONAL_QUOTES = [
    "Every sentence you speak is a step forward. Keep going! 💪",
    "Mistakes aren't failures — they're just your brain learning faster. 🧠",
    "The best polyglots were once terrible beginners. You're on the right path. 🌟",
    "Even 10 minutes of practice a day beats a 2-hour session once a week. ⏱️",
    "Language opens doors that no key can. Keep unlocking! 🗝️",
    "You're literally rewiring your brain right now. That's extraordinary. ✨",
    "Confidence in a new language comes from repetition, not perfection. 🔄",
]

MISTAKE_TIPS = {
    "grammar":       "Try rewriting tricky sentences 3 times with slight variations — repetition cements grammar rules.",
    "vocabulary":    "Attach new words to vivid mental images or personal memories for better recall.",
    "pronunciation": "Record yourself, then compare it to a native speaker clip. The gap closes fast.",
    "spelling":      "Dictation exercises work incredibly well — listen and type, don't look.",
    "idioms":        "Learn idioms through stories or movies, not just isolated lists.",
    "cultural":      "Follow social media accounts from that country — real-world context beats textbooks.",
}


# ── Database Layer ─────────────────────────────────────────────────────────────

def get_db_connection():
    """Open (or create) the SQLite DB. Runs once per session."""
    conn = sqlite3.connect(r"C:\Users\TANMAY VIJAYVARGIYA\Downloads\New version AI Chatbot\language_learning.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def setup_database(conn):
    """
    Create all required tables if they don't exist yet.
    Using IF NOT EXISTS means this is safe to call every startup.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mistakes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date  TEXT    NOT NULL,
            language      TEXT    NOT NULL,
            mistake_type  TEXT    NOT NULL,
            original_text TEXT    NOT NULL,
            corrected_text TEXT   NOT NULL,
            explanation   TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_stats (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date   TEXT NOT NULL,
            language       TEXT NOT NULL,
            messages_sent  INTEGER DEFAULT 0,
            duration_mins  REAL DEFAULT 0
        )
    """)

    conn.commit()


def save_mistake(conn, language, mistake_type, original, corrected, explanation):
    """Persist a detected mistake to the DB."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mistakes (session_date, language, mistake_type, original_text, corrected_text, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d"), language, mistake_type, original, corrected, explanation))
    conn.commit()


def fetch_mistake_summary(conn, language):
    """Return a count of each mistake type for the given language."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mistake_type, COUNT(*) as total
        FROM mistakes
        WHERE language = ?
        GROUP BY mistake_type
        ORDER BY total DESC
    """, (language,))
    return {row["mistake_type"]: row["total"] for row in cursor.fetchall()}


def fetch_recent_mistakes(conn, language, limit=5):
    """Pull the last N mistakes for review."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT original_text, corrected_text, explanation, session_date
        FROM mistakes
        WHERE language = ?
        ORDER BY id DESC
        LIMIT ?
    """, (language, limit))
    return cursor.fetchall()


# ── LLM / AI Layer ─────────────────────────────────────────────────────────────

def build_llm(api_key: str) -> ChatGroq:
    """
    Initialize Groq LLM.

    WHY GROQ?
    - Completely free tier for testing (no credit card needed for dev)
    - llama-3.3-70b-versatile is genuinely good at language tutoring
    - Latency is insanely low compared to OpenAI for the same model size
    - API format is almost identical to OpenAI so switching later is trivial

    Get your free key at: https://console.groq.com
    Other free models you can swap in:
      - gemma2-9b-it          (Google's Gemma 2, fast and capable)
      - mixtral-8x7b-32768    (great for multilingual tasks)
      - llama-3.1-8b-instant  (ultra-fast, decent quality)
    """
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024,
    )


def build_system_prompt(learning_lang: str, native_lang: str, level: str, scene: str) -> str:
    """
    Craft a detailed system prompt. The more specific this is, the better
    the model performs. Vague prompts give generic tutors; specific ones
    give genuinely helpful, character-rich tutors.
    """
    level_name = level.split(" ", 1)[-1]  # strip emoji

    return f"""You are a warm, encouraging language tutor named Léa.

Your student speaks {native_lang} natively and is learning {learning_lang} at a {level_name} level.
Today's conversation practice scene: "{scene}"

Your job:
1. Hold a natural, flowing conversation IN {learning_lang} around the scene above.
2. After each student message, gently note any grammar, vocabulary, or spelling mistakes.
   Format corrections clearly at the end of your reply like this:
   ---
   📝 Quick correction: "[their error]" → "[correct form]"
   💡 Why: [1-sentence explanation]
   ---
3. If they write in {native_lang}, kindly encourage them to try in {learning_lang} instead,
   and offer a helpful starter phrase.
4. Adapt your vocabulary and sentence complexity strictly to {level_name} level.
5. Ask follow-up questions to keep the conversation going naturally.
6. Every 3–4 messages, slip in one interesting cultural fact about a country where {learning_lang} is spoken.
7. Stay warm, patient, and never make the student feel embarrassed.

Remember: your primary goal is to build their confidence, not just correct errors."""


def extract_corrections(response_text: str):
    """
    Parse any corrections the LLM embedded in its response.
    Returns a list of (original, corrected, explanation) tuples.
    This is intentionally loose regex — the model doesn't always format perfectly.
    """
    corrections = []

    # Match our formatted correction block
    pattern = r'📝 Quick correction:\s*"([^"]+)"\s*→\s*"([^"]+)"\s*\n\s*💡 Why:\s*(.+?)(?=\n---|$)'
    matches = re.findall(pattern, response_text, re.DOTALL)

    for original, corrected, explanation in matches:
        corrections.append((
            original.strip(),
            corrected.strip(),
            explanation.strip()
        ))

    return corrections


def generate_response(llm, history: list, system_prompt: str, user_message: str):
    """
    Call the LLM with full conversation history.
    Returns the full AIMessage object (we use .content for text).
    """
    messages = [SystemMessage(content=system_prompt)] + history + [HumanMessage(content=user_message)]

    try:
        response = llm.invoke(messages)
        return response
    except Exception as err:
        # Return a fake AIMessage-like object so callers don't need to branch
        error_msg = f"🤖 Couldn't reach the AI right now. Error: {str(err)}"
        return AIMessage(content=error_msg)


def generate_vocabulary_lesson(llm, language: str, level: str, topic: str) -> str:
    """
    Generate a structured mini-vocabulary lesson on demand.
    Kept separate from the chat so it doesn't pollute conversation history.
    """
    level_name = level.split(" ", 1)[-1]
    prompt = f"""Create a compact vocabulary lesson for a {level_name} learner of {language}.
Topic: {topic}

Include:
- 6 useful words/phrases with translations
- 2 example sentences for each
- 1 memory tip per word
Keep it concise and practical. Format clearly."""

    messages = [HumanMessage(content=prompt)]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as err:
        return f"Couldn't generate lesson: {str(err)}"


def generate_grammar_drill(llm, language: str, level: str, grammar_point: str) -> str:
    """Produce a short fill-in-the-blank or translation drill."""
    level_name = level.split(" ", 1)[-1]
    prompt = f"""Create a quick grammar drill for a {level_name} learner of {language}.
Grammar point: {grammar_point}

Give 5 short exercises. For each:
1. Show the exercise (fill-in-blank or translate)
2. Then show the answer and a brief explanation.
Keep it practical and encouraging."""

    messages = [HumanMessage(content=prompt)]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as err:
        return f"Couldn't generate drill: {str(err)}"


# ── Streamlit UI ────────────────────────────────────────────────────────────────

def render_sidebar(conn):
    """
    All setup and config lives in the sidebar.
    Returns a dict of settings if the user clicked Start, else None.
    """
    st.sidebar.title("🌍 Language Tutor Setup")
    st.sidebar.markdown("---")

    api_key = st.sidebar.text_input(
        "Groq API Key 🔑",
        type="password",
        help="Free at console.groq.com — takes 30 seconds to get one.",
    )

    st.sidebar.markdown("**Your Learning Setup**")

    learning_lang_emoji = st.sidebar.selectbox("Language to Learn", list(LANGUAGES.keys()))
    native_lang_emoji = st.sidebar.selectbox("Your Native Language", list(NATIVE_LANGUAGES.keys()))
    level = st.sidebar.selectbox("Your Level", LEVELS)

    st.sidebar.markdown("---")
    start_clicked = st.sidebar.button("🚀 Start Session", use_container_width=True)

    if start_clicked:
        if not api_key:
            st.sidebar.error("Please enter your Groq API key first.")
            return None
        return {
            "api_key": api_key,
            "learning_language": LANGUAGES[learning_lang_emoji],
            "learning_language_display": learning_lang_emoji,
            "native_language": NATIVE_LANGUAGES[native_lang_emoji],
            "level": level,
        }

    # ── Progress & Insights (only visible after session starts) ──
    if st.session_state.get("session_active") and "settings" in st.session_state:
        lang = st.session_state.settings["learning_language"]
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📊 Your Progress**")

        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.sidebar.metric("Messages sent this session", msg_count)

        mistake_counts = fetch_mistake_summary(conn, lang)
        if mistake_counts:
            st.sidebar.markdown("**Common mistake areas:**")
            for mtype, count in mistake_counts.items():
                st.sidebar.progress(
                    min(count / 10, 1.0),
                    text=f"{mtype.capitalize()} ({count}×)"
                )
        else:
            st.sidebar.info("No mistakes logged yet. Keep chatting!")

    return None


def render_tools_tab(llm, settings: dict):
    """
    Extra tools: vocabulary builder and grammar drills.
    Kept in a separate tab so they don't clutter the chat.
    """
    lang = settings["learning_language"]
    level = settings["level"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 Vocabulary Builder")
        vocab_topic = st.text_input("Enter a topic (e.g. 'travel', 'food', 'emotions')")
        if st.button("Generate Lesson", key="vocab_btn") and vocab_topic:
            with st.spinner("Building your vocab lesson..."):
                lesson = generate_vocabulary_lesson(llm, lang, level, vocab_topic)
            st.markdown(lesson)

    with col2:
        st.markdown("### ✏️ Grammar Drills")
        grammar_point = st.text_input("Grammar topic (e.g. 'past tense', 'articles', 'gender')")
        if st.button("Generate Drill", key="grammar_btn") and grammar_point:
            with st.spinner("Preparing your drill..."):
                drill = generate_grammar_drill(llm, lang, level, grammar_point)
            st.markdown(drill)


def render_mistakes_tab(conn, language: str):
    """Display recent mistake history for review."""
    st.markdown("### 🔍 Recent Corrections")

    recent = fetch_recent_mistakes(conn, language, limit=10)
    if not recent:
        st.info("No corrections logged yet. Start chatting and mistakes will appear here for review!")
        return

    for row in recent:
        with st.expander(f"❌ {row['original_text']} → ✅ {row['corrected_text']}"):
            st.markdown(f"**Why:** {row['explanation']}")
            st.caption(f"Logged on {row['session_date']}")

    st.markdown("---")
    st.markdown("### 💡 Improvement Tips")
    mistake_counts = fetch_mistake_summary(conn, language)
    if mistake_counts:
        top_mistake = max(mistake_counts, key=mistake_counts.get)
        tip = MISTAKE_TIPS.get(top_mistake, "Keep practicing consistently!")
        st.info(f"**Your focus area: {top_mistake.capitalize()}**\n\n{tip}")


def main():
    st.set_page_config(
        page_title="AI Language Tutor",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Initialize session state ────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []     # LangChain message objects
    if "session_active" not in st.session_state:
        st.session_state.session_active = False
    if "scene" not in st.session_state:
        st.session_state.scene = None

    # ── DB setup (runs once per server process, not per request) ───────────────
    conn = get_db_connection()
    setup_database(conn)

    # ── Sidebar (config + stats) ────────────────────────────────────────────────
    new_settings = render_sidebar(conn)

    if new_settings:
        # User clicked "Start Session" with valid inputs
        st.session_state.settings = new_settings
        st.session_state.session_active = True
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.scene = random.choice(SCENES[new_settings["level"]])

        llm = build_llm(new_settings["api_key"])
        st.session_state.llm = llm

        # Warm welcome message from the tutor
        scene = st.session_state.scene
        lang_display = new_settings["learning_language_display"]
        level = new_settings["level"]
        welcome = (
            f"👋 Welcome! I'm Léa, your {lang_display} tutor today.\n\n"
            f"We're practicing at **{level}** level. Your scenario: **{scene}**\n\n"
            f"Go ahead and start us off — I'll guide you, correct gently, and keep it fun! 😊"
        )
        st.session_state.messages.append({"role": "assistant", "content": welcome})

    # ── Main content area ────────────────────────────────────────────────────────
    if not st.session_state.session_active:
        # Landing / onboarding state
        st.title("🌍 AI Language Tutor")
        st.markdown(
            """
            Practice speaking any language with an AI tutor that:
            - Holds **real conversations** in your target language
            - **Gently corrects** mistakes and explains why
            - Tracks your **common errors** over time
            - Offers **vocabulary lessons** and **grammar drills** on demand
            - Teaches **cultural context**, not just textbook phrases

            ---
            👈 **Set up your session in the sidebar to get started.**

            > **Free to use**: This app runs on [Groq](https://console.groq.com) — get your free API key in under a minute.
            > Model used: `llama-3.3-70b-versatile` (fast, multilingual, excellent for tutoring)
            """
        )
        return

    # ── Active session ─────────────────────────────────────────────────────────
    settings = st.session_state.settings
    llm = st.session_state.llm
    lang = settings["learning_language"]

    st.title(f"💬 Learning {settings['learning_language_display']}")
    st.caption(f"Scene: {st.session_state.scene} · Level: {settings['level']}")

    # Tabs: Chat | Tools | Mistake Log
    tab_chat, tab_tools, tab_mistakes = st.tabs(["💬 Conversation", "🛠️ Practice Tools", "📋 Mistake Log"])

    with tab_chat:
        # ── Message history display ────────────────────────────────────────────
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ── Input box ─────────────────────────────────────────────────────────
        user_input = st.chat_input(f"Type in {lang} (or ask anything about it)...")

        if user_input:
            # Show user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Build system prompt fresh each time (settings could change in theory)
            system_prompt = build_system_prompt(
                lang,
                settings["native_language"],
                settings["level"],
                st.session_state.scene,
            )

            # Call the LLM
            with st.chat_message("assistant"):
                with st.spinner("Léa is thinking..."):
                    response = generate_response(
                        llm,
                        st.session_state.history,
                        system_prompt,
                        user_input,
                    )
                reply_text = response.content
                st.markdown(reply_text)

            # Update LangChain history (keep last 20 turns to avoid token bloat)
            st.session_state.history.append(HumanMessage(content=user_input))
            st.session_state.history.append(AIMessage(content=reply_text))
            if len(st.session_state.history) > 40:
                st.session_state.history = st.session_state.history[-40:]

            # Persist to display history
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

            # Extract and save any corrections the model included
            corrections = extract_corrections(reply_text)
            for original, corrected, explanation in corrections:
                # Simple heuristic: classify mistake type by keywords in the explanation
                m_type = "grammar"
                for keyword in ["spell", "spelling", "typo"]:
                    if keyword in explanation.lower():
                        m_type = "spelling"
                        break
                for keyword in ["vocabulary", "word choice", "phrase"]:
                    if keyword in explanation.lower():
                        m_type = "vocabulary"
                        break
                for keyword in ["idiom", "expression"]:
                    if keyword in explanation.lower():
                        m_type = "idioms"
                        break
                save_mistake(conn, lang, m_type, original, corrected, explanation)

        # ── Motivational quote at the bottom ──────────────────────────────────
        st.markdown("---")
        st.caption(random.choice(MOTIVATIONAL_QUOTES))

        # ── Quick action buttons ───────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎲 New Scene", help="Switch to a different practice scenario"):
                st.session_state.scene = random.choice(SCENES[settings["level"]])
                st.session_state.history = []   # fresh history for new scene
                new_scene_msg = f"🔄 New scene: **{st.session_state.scene}** — let's pick up there!"
                st.session_state.messages.append({"role": "assistant", "content": new_scene_msg})
                st.rerun()
        with col2:
            if st.button("🔄 Clear Chat", help="Start the conversation fresh"):
                st.session_state.messages = []
                st.session_state.history = []
                st.rerun()
        with col3:
            if st.button("💾 Export Chat", help="Download conversation as text"):
                chat_export = "\n\n".join(
                    f"[{m['role'].upper()}]: {m['content']}"
                    for m in st.session_state.messages
                )
                st.download_button(
                    "📥 Download",
                    data=chat_export,
                    file_name=f"{lang}_practice_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                )

    with tab_tools:
        render_tools_tab(llm, settings)

    with tab_mistakes:
        render_mistakes_tab(conn, lang)


if __name__ == "__main__":
    main()
