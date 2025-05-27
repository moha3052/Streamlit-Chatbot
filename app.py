from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Streamlit Chatbot 💬")

# Initialiser sessionstilstand
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

# Formular til personlig info
if not st.session_state.setup_complete:
    st.subheader('Personlige oplysninger', divider='rainbow')

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(
        label="Navn", max_chars=40, value=st.session_state["name"], placeholder="Indtast dit navn"
    )

    st.session_state["experience"] = st.text_area(
        label="Erfaring", max_chars=200, value=st.session_state["experience"],
        placeholder="Beskriv din erfaring"
    )

    st.session_state["skills"] = st.text_area(
        label="Færdigheder", max_chars=200, value=st.session_state["skills"],
        placeholder="Skriv dine færdigheder"  
    )

   

    st.subheader('Virksomhed og stilling', divider='rainbow')

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Frontend Udvikler"
    if "company" not in st.session_state:
        st.session_state["company"] = "Google"

    col1, col2 = st.columns(2)

    with col1:
        st.session_state["level"] = st.radio(
            "Vælg niveau",
            key="visibility",
            options=["Junior", "Mid", "Senior"],
        )
    with col2:
        st.session_state["position"] = st.selectbox(
            "Vælg stilling",
            ("Frontend Udvikler","Backend Udvikler","Fullstack Udvikler","Dataanalytiker",
             "Dataingeniør","DevOps Ingeniør","UX/UI Designer","Projektleder","Cloud Ingeniør",
             "AI-udvikler","Mobiludvikler","Softwareudvikler","Webudvikler","IT-konsulent")
        )

    st.session_state["company"] = st.text_input(
        "Indtast virksomhedens navn",
        value=st.session_state["company"],
        placeholder="f.eks. Google, Apple, Amazon, Microsoft, Tesla"
    )



    if st.button("Start interview", on_click=complete_setup):
        st.write("Opsætning fuldført. Starter interview...")

# Interview-funktionalitet
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info("Start med at præsentere dig selv:", icon="👋")

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system", 
            "content": (
                f"Du er en HR-medarbejder, som interviewer en ansøger ved navn {st.session_state['name']}. "
                f"Hun/han har erfaring: {st.session_state['experience']} og færdigheder: {st.session_state['skills']}. "
                f"Du interviewer til stillingen som {st.session_state['level']} {st.session_state['position']} "
                f"hos virksomheden {st.session_state['company']}."
            )}
        ]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Dit svar.", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
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

            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Feedback-funktion
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
    )

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    try:
        feedback_completion = feedback_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful tool that provides feedback on an interviewee's performance.
                    Before the feedback, give a score from 1 to 10.
                    Follow this format:
                    Overall Score: //Your score
                    Feedback: //Here you put your feedback
                    Give only the feedback, do not ask any additional questions.
                    """
                },
                {
                    "role": "user",
                    "content": f"This is the interview you need to evaluate:\n\n{conversation_history}"
                }
            ]
        )
        st.write(feedback_completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Der opstod en fejl under feedbackgenerering: {e}")

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")