import streamlit as st
import requests

st.set_page_config(page_title="הבוט של נעם", layout="centered")

# שליפת המפתח מה-Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 ברוך הבא!")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.username = name
            st.rerun()
    st.stop()

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

    # כתובת ה-API הרשמית
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if "candidates" in result:
            bot_text = result["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
        else:
            # אם יש שגיאה, נציג אותה בצורה ברורה
            error_msg = result.get('error', {}).get('message', 'מפתח ה-API לא תקין או חסום')
            st.error(f"שגיאה מגוגל: {error_msg}")
            if "API key not valid" in error_msg:
                st.info("יאיר, נראה שצריך להחליף את המפתח ב-Secrets!")
    except Exception as e:
        st.error(f"תקלה בחיבור: {str(e)}")
