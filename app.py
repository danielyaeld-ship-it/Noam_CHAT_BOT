import streamlit as st
import requests

# הגדרות דף
st.set_page_config(page_title="הבוט של נעם", layout="centered")

# שליפת המפתח מה-Secrets (חובה להגדיר ב-Streamlit Cloud)
api_key = st.secrets.get("GOOGLE_API_KEY")

# --- שלב 1: בקשת שם המשתמש (כפי שביקשת) ---
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.title("🤖 ברוך הבא לבוט המיוחד!")
    name = st.text_input("איך קוראים לך?", key="name_input")
    if st.button("בוא נתחיל"):
        if name.strip():
            st.session_state.username = name.strip()
            st.rerun()
    st.stop() # עוצר כאן עד שמכניסים שם

# --- שלב 2: ממשק הצ'אט ---
st.title(f"שלום {st.session_state.username} 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריית ההודעות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("שאל אותי משהו..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- התיקון הקריטי: פנייה ישירה לשרת של גוגל ---
    # הכתובת הזו עוקפת את שגיאת ה-404 של v1beta
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        if "candidates" in result:
            bot_text = result["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
        else:
            # אם יש שגיאה במפתח או במודל
            error_msg = result.get('error', {}).get('message', 'שגיאה לא ידועה')
            st.error(f"השרת של גוגל החזיר שגיאה: {error_msg}")
    except Exception as e:
        st.error(f"תקלה בחיבור: {str(e)}")
