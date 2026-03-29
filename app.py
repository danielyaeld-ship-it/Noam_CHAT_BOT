import streamlit as st
import google.generativeai as genai

# הגדרת המפתח מה-Secrets
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("הבוט של יאיר התותח 🤖")

# יצירת המודל
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("דבר אלי..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        # אם יש שגיאה, נציג אותה בצורה ברורה
        st.error(f"גוגל אומר שיש בעיה במפתח: {e}")
