import streamlit as st
import google.generativeai as genai

# הגדרת דף בסיסית
st.set_page_config(page_title="AI Super Bot", layout="wide")

# חיבור למפתח ה-API מה-Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("לא נמצא מפתח API ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# פתרון ה-404: שימוש בשם המודל המלא ללא הקידומת הבעייתית
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

st.title("🤖 הבוט של נעם")

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריית הצ'אט
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("מה תרצה לשאול?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            # יצירת התשובה
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        # הצגת שגיאה ידידותית אם המודל עדיין עושה בעיות
        st.error(f"אופס, משהו השתבש: {str(e)}")
