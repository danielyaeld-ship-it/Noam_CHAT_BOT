import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os 

# --- הגדרות דף להתאמה לנייד ---
st.set_page_config(page_title="AI Super Bot", layout="wide")

# --- פונקציות זיכרון (Caching) להאצה ---
@st.cache_resource
def init_gemini():
    # המפתח שלך - מוטמע ישירות כדי למנוע תקלות חיבור
    api_key = st.secrets.get("GOOGLE_API_KEY") or "AIzaSyAodfN_aB3GQ53mkI9hXhp9Y9OUhWBCews"
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # שימוש בשם המודל המדויק ללא תוספות
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            st.error(f"שגיאה באתחול המודל: {e}")
    return None

@st.cache_data
def parse_pdf(file_bytes):
    try:
        reader = PdfReader(file_bytes)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        words = text.split()
        # מחלק את הטקסט למקטעים של 700 מילים
        return [" ".join(words[i:i+700]) for i in range(0, len(words), 700)]
    except Exception:
        return []

# --- אתחול משתנים ב-Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb" not in st.session_state:
    st.session_state.kb = []

# אתחול המודל
model = init_gemini()

# --- ממשק משתמש ---
st.title("🤖 הבוט של נעם")

# סרגל צד לניהול קבצים
with st.sidebar:
    st.header("ניהול קבצים")
    files = st.file_uploader("העלה קבצי PDF", type="pdf", accept_multiple_files=True)
    if files:
        new_kb = []
        for f in files:
            new_kb.extend(parse_pdf(f))
        st.session_state.kb = new_kb
        st.success("הקבצים נטענו בהצלחה!")

# הצגת היסטוריית השיחה
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# תיבת קלט מהמשתמש
user_input = st.chat_input("שאל אותי משהו...")

if user_input:
    # הוספת הודעת המשתמש להיסטוריה והצגתה
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # יצירת תשובה מהמודל
    if model:
        with st.chat_message("assistant"):
            with st.spinner("חושב על תשובה..."):
                try:
                    # שימוש במידע מה-PDF כהקשר (Context) אם קיים
                    context = "\n".join(st.session_state.kb[-3:])
                    full_prompt = f"Context: {context}\n\nUser: {user_input}" if context else user_input
                    
                    response = model.generate_content(full_prompt)
                    answer = response.text
                    
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"שגיאה ביצירת התשובה: {e}")
    else:
        st.error("המודל לא הוגדר. וודא שחנית מפתח API תקין.")
