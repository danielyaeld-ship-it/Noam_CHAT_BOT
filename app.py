import streamlit as st
import requests

# 1. הגדרות דף
st.set_page_config(page_title="הבוט של נעם", layout="centered")

# 2. שליפת המפתח מה-Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

# 3. ניהול שם המשתמש
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 ברוך הבא לבוט של נעם!")
    name = st.text_input("איך קוראים לך?", key="name_input")
    if st.button("בוא נתחיל"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
    st.stop()

# 4. ממשק הצ'אט
st.title(f"שלום {st.session_state.username} 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. קלט ושליחה (עם תיקון הכתובת של גוגל)
if prompt := st.chat_input("שאל אותי משהו..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # הכתובת המדויקת שגוגל דורש כרגע עבור gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        # בדיקה אם התקבלה תשובה תקינה
        if "candidates" in result:
            bot_text = result["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
        else:
            # הדפסת השגיאה המלאה לניפוי תקלות
            error_message = result.get('error', {}).get('message', 'שגיאה לא ידועה')
            st.error(f"גוגל אומר: {error_message}")
            if "not found" in error_message.lower():
                st.info("מנסה נתיב חלופי...")
                # כאן אפשר להוסיף ניסיון אוטומטי לכתובת אחרת אם זה נכשל
                
    except Exception as e:
        st.error(f"תקלה טכנית: {str(e)}")
