import streamlit as st
import google.generativeai as genai

# הגדרת המפתח מה-Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🤖 הבוט של נעם")

# הגדרת המודל בצורה חסינה
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת צ'אט
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט משתמש
if prompt := st.chat_input("מה תרצה לשאול?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # כאן התיקון - הוספנו מנגנון למניעת ה-404
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
