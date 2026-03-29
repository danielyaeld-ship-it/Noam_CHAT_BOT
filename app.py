import streamlit as st
import google.generativeai as genai

# --- הגדרות דף ---
st.set_page_config(page_title="AI Super Bot", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- עיצוב ---
bg_color = "#121212" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#000000"

st.markdown(f"""
<style>
.stApp {{ background-color: {bg_color}; color: {text_color}; }}
.user-msg {{ background-color: #A0E7E5; border-radius: 15px; padding: 12px; margin-bottom: 10px; color: black; display: inline-block; }}
.bot-msg {{ background-color: #FFAEBC; border-radius: 15px; padding: 12px; margin-bottom: 10px; color: black; display: inline-block; }}
</style>
""", unsafe_allow_html=True)

# --- חיבור API חסין שגיאות ---
@st.cache_resource
def init_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # שימוש בשם המודל המלא כדי לעקוף את שגיאת ה-v1beta
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
            return model
        except Exception as e:
            st.error(f"שגיאה בחיבור: {e}")
    return None

model = init_gemini()

# --- ניהול משתמש ---
if "username" not in st.session_state: 
    st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 הבוט של נעם")
    name_input = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name_input:
            st.session_state.username = name_input
            st.rerun()
    st.stop()

# --- ממשק הצ'אט ---
st.title(f"שלום {st.session_state.username} 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

# תפריט צד
with st.sidebar:
    if st.button("💡 מצב יום/לילה"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    if st.button("🗑️ נקה שיחה"):
        st.session_state.messages = []
        st.rerun()

# הצגת הודעות
for msg in st.session_state.messages:
    align = "left" if msg["role"] == "user" else "right"
    cls = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f"<div style='text-align: {align}'><div class='{cls}'>{msg['content']}</div></div>", unsafe_allow_html=True)

# קלט מהמשתמש
user_input = st.chat_input("כתוב הודעה...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    if model:
        try:
            # יצירת תשובה
            response = model.generate_content(user_input)
            st.session_state.messages.append({"role": "bot", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בייצור תשובה: {e}")
