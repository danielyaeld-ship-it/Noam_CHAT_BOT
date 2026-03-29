import streamlit as st
import google.generativeai as genai

# הגדרת כותרת האתר
st.set_page_config(page_title="הבוט של יאיר התותח", layout="centered")

# שליפת המפתח מה-Secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("שכחת להגדיר את המפתח ב-Secrets!")
    st.stop()

st.title("🤖 הבוט של יאיר התותח")

# אתחול היסטוריית הצ'אט
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת ההודעות הקודמות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת קלט למשתמש
if prompt := st.chat_input("דבר אלי..."):
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # יצירת תשובה מהמודל
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # הצגת תשובת הבוט
        with st.chat_message("assistant"):
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    except Exception as e:
        if "API_KEY_INVALID" in str(e):
            st.error("ה-API Key שלך לא תקין. צור מפתח חדש ב-AI Studio בלי לצלם אותו!")
        else:
            st.error(f"תקלה טכנית: {e}")
