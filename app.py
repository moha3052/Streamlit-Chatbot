from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Streamlit Chatbot 💬")

st.subheader('Personal information', divider='rainbow')

name = st.text_input(label="name", max_chars=None, placeholder="Enter your name")

experience = st.text_area(label="Expirience", value= "", height = None, max_chars=None, placeholder="Describe your experience")

skills = st.text_area(label="Skills", value="", height = None, max_chars=None, placeholder="List your skills")

st.write(f"**Your Name**: {name}")
st.write(f"**Your Experience**: {experience}")
st.write(f"**Your skills**: {skills}")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Your answer."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})