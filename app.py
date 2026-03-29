import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- הגדרות דף ---
st.set_page_config(page_title="AI Super Bot", layout="wide")

# --- פונקציות ליבה ---
@st.cache_resource
def init_gemini():
    # המפתח שלך - מוטמע ישירות למניעת תקלות
    api_key = st.secrets.get("GOOGLE_API_KEY") or "AIzaSyAodfN_aB3GQ53mkI9hXhp9Y9OUhWBCews"
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # פתרון ה-404: שימוש ב-model_name מפורש ללא תחילית models/
            return genai.GenerativeModel(model_name="gemini-1.5-flash")
        except Exception as e:
            st.error(f"שגיאה באתחול: {e}")
    return None

@st.cache_data
def parse_pdf(file_bytes):
    try:
        reader = PdfReader(file_bytes)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        words = text.split()
        return [" ".join(words[i:i+700]) for i in range(0, len(words), 700)]
    except Exception:
        return []

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb" not in st.session_state:
    st.session_state.kb = []

model = init_gemini()

# --- ממשק משתמש ---
st.title("🤖 הבוט של נעם")

with st.sidebar:
    st.header("ניהול קבצים")
    files = st.file_uploader("העלה PDF", type="pdf", accept_multiple_files=True)
    if files:
        new_kb = []
        for f in files:
            new_kb.extend(parse_pdf(f))
        st.session_state.kb = new_kb
        st.success("הקבצים נטענו!")

# הצגת היסטוריה בפורמט צ'אט
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# קלט מהמשתמש
user_input = st.chat_input("שאל אותי משהו...")

if user_input:
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    if model:
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                try:
                    # הוספת הקשר מה-PDF
                    context = "\n".join(st.session_state.kb[-3:])
                    full_prompt = f"Context: {context}\n\nUser: {user_input}" if context else user_input
                    
                    # יצירת התשובה
                    response = model.generate_content(full_prompt)
                    answer = response.text
                    
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"שגיאה ביצירת תשובה: {e}")
                    st.info("נסה לנקות את ה-Cache בתפריט צד ימין למעלה.")
    else:
        st.error("המודל לא מחובר. בדוק את ה-API Key ב-Secrets.")
