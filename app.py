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
    st.title("🤖 שלום! בוא נתחיל")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.username = name
            st.rerun()
    st.stop()

# 4. ממשק הצ'אט
st.title(f"שלום {st.session_state.username} 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. שליחה לגוגל - הגרסה שעוקפת את השגיאה
if prompt := st.chat_input("שאל אותי משהו..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # שימוש במודל gemini-pro - הוא הכי יציב בחיבורים ישירים
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
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
            # אם גוגל מחזיר שגיאה, נציג אותה בצורה ברורה
            st.error(f"גוגל לא עונה: {result.get('error', {}).get('message', 'תקלה לא ידועה')}")
    except Exception as e:
        st.error(f"שגיאה בחיבור: {str(e)}")
