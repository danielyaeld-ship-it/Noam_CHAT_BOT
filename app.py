import streamlit as st
import requests
import json

# הגדרות דף
st.set_page_config(page_title="הבוט של נעם", layout="centered")

# שליפת המפתח
api_key = st.secrets.get("GOOGLE_API_KEY")

# ניהול שם המשתמש
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

    # הכתובת המדויקת והחדשה ביותר של גוגל
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        result = response.json()
        
        if "candidates" in result:
            bot_text = result["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
        else:
            # כאן אנחנו נראה בדיוק מה הבעיה
            error_details = result.get('error', {})
            error_msg = error_details.get('message', 'שגיאה לא ידועה')
            st.error(f"גוגל אומר: {error_msg}")
            
    except Exception as e:
        st.error(f"שגיאה בחיבור: {str(e)}")
