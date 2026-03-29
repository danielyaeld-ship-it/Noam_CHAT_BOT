     import streamlit as st
import google.generativeai as genai

# --- הגדרות דף ---
st.set_page_config(page_title="AI Super Bot", layout="wide", initial_sidebar_state="collapsed")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- עיצוב ומצב לילה ---
bg_color = "#121212" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#000000"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg_color}; color: {text_color}; }}
.user-msg {{ background-color: #A0E7E5; border-radius: 15px; padding: 12px; margin-bottom: 10px; color: black; display: inline-block; max-width: 80%; }}
.bot-msg {{ background-color: #FFAEBC; border-radius: 15px; padding: 12px; margin-bottom: 10px; color: black; display: inline-block; max-width: 80%; }}
</style>
""", unsafe_allow_html=True)

# --- חיבור API בטוח (Secrets) ---
@st.cache_resource
def init_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            st.error(f"שגיאה בחיבור: {e}")
    return None

model = init_gemini()

# --- שם משתמש ---
if "username" not in st.session_state: st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 הבוט של נעם - ברוכים הבאים!")
    name_input = st.text_input("איך קוראים לך?", placeholder="הכנס שם...")
    if st.button("בוא נתחיל"):
        if name_input.strip():
            st.session_state.username = name_input.strip()
            st.rerun()
    st.stop()

username = st.session_state.username

# --- תפריט צד ---
with st.sidebar:
    st.write(f"משתמש מחובר: **{username}**")
    if st.button("💡 החלף מצב יום/לילה"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    if st.button("🔄 החלף משתמש"):
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()

# --- ניהול הודעות ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title(f"שלום {username} 👋")

# הצגת היסטוריה
for msg in st.session_state.messages:
    div_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    align = "left" if msg["role"] == "user" else "right"
    st.markdown(f"<div style='text-align: {align}'><div class='{div_class}'>{msg['content']}</div></div>", unsafe_allow_html=True)

# --- קלט משתמש ---
user_input = st.chat_input("שאל אותי משהו...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    if model:
        try:
            context = "\n".join([m["content"] for m in st.session_state.messages[-3:]])
            response = model.generate_content(f"User Name: {username}\nContext: {context}\nQuestion: {user_input}")
            st.session_state.messages.append({"role": "bot", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")
