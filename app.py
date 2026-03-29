import streamlit as st
from streamlit_chat import message
import google.generativeai as genai
from PyPDF2 import PdfReader
import os 

# --- הגדרות דף להתאמה לנייד ---
st.set_page_config(page_title="AI Super Bot", layout="wide", initial_sidebar_state="collapsed")

# --- פונקציות זיכרון (Caching) להאצה ---
@st.cache_resource
def init_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY") 
    if api_key:
        genai.configure(api_key=api_key)
        # שים לב לשם המדויק כאן:
        return genai.GenerativeModel("gemini-1.5-flash")
    return None
    return None
def parse_pdf(file_bytes):
    try:
        reader = PdfReader(file_bytes)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        words = text.split()
        return [" ".join(words[i:i+700]) for i in range(0, len(words), 700)]
    except:
        return []

# --- אתחול משתנים ---
model = genai.GenerativeModel('gemini-1.5-flash')
model = init_gemini()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "kb" not in st.session_state:
    st.session_state.kb = []

# --- ממשק משתמש ---
st.title("🤖 הבוט של נעם")

with st.sidebar:
    st.header("ניהול קבצים")
    files = st.file_uploader("העלה PDF", type="pdf", accept_multiple_files=True)
    if files:
        for f in files:
            st.session_state.kb.extend(parse_pdf(f))
        st.success("הקבצים נטענו!")

# תצוגת הודעות
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=(msg["role"] == "user"), key=f"m_{i}")

# קלט מהמשתמש
user_input = st.chat_input("שאל אותי משהו...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # חיווי "חושב" בצד
    with st.status("מעבד בקשה...", expanded=False) as status:
        st.write("סורק נתונים...")
        context = "\n".join(st.session_state.kb[-3:])
        prompt = f"Context: {context}\n\nUser: {user_input}" if context else user_input
        
        st.write("מייצר תשובה...")
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "bot", "content": response.text})
        status.update(label="בוצע!", state="complete")
    
    st.rerun()
