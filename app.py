import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="AI Super Bot", layout="wide")

@st.cache_resource
def init_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY") or "AIzaSyAodfN_aB3GQ53mkI9hXhp9Y9OUhWBCews"
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # פקודה שבודקת איזה מודלים זמינים לך ובוחרת את הראשון שעובד
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
        except Exception as e:
            st.error(f"שגיאה באתחול: {e}")
    return None

# --- שאר הקוד המוכר ---
if "messages" not in st.session_state: st.session_state.messages = []
if "kb" not in st.session_state: st.session_state.kb = []

model = init_gemini()
st.title("🤖 הבוט של נעם")

with st.sidebar:
    files = st.file_uploader("העלה PDF", type="pdf", accept_multiple_files=True)
    if files:
        text = ""
        for f in files:
            reader = PdfReader(f)
            for page in reader.pages: text += page.extract_text()
        st.session_state.kb = [text]
        st.success("נטען!")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

user_input = st.chat_input("שאל אותי משהו...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)
    
    if model:
        with st.chat_message("assistant"):
            try:
                context = st.session_state.kb[0] if st.session_state.kb else ""
                response = model.generate_content(f"{context}\n\n{user_input}")
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"שגיאה: {e}")
