import streamlit as st
import google.generativeai as genai
from google.api_core import client_options

# הגדרת דף
st.set_page_config(page_title="הבוט של נעם", layout="centered")

# הגדרת מפתח ה-API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets!")
    st.stop()

# --- התיקון הקריטי למניעת 404 ---
# אנחנו מכריחים את הבוט להשתמש בגרסה היציבה (v1) ולא ב-v1beta
options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], client_options=options)

@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

# --- ניהול שם משתמש ---
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 ברוכים הבאים!")
    name = st.text_input("איך קוראים לך?")
    if st.button("בוא נתחיל"):
        if name:
            st.session_state.username = name
            st.rerun()
    st.stop()

# --- ממשק הצ'אט ---
st.title(f"שלום {st.session_state.username} 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("שאל אותי משהו..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            # שימוש בגרסה היציבה בלבד
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"אופס, משהו השתבש: {str(e)}")
