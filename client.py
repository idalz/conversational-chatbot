import streamlit as st
import requests
import time
import secrets


# Streamed response emulator
def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat")

# Initialize session key
if "key" not in st.session_state:
    st.session_state.key = secrets.token_urlsafe(16)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Message...?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Make a POST request to the FastAPI server
        response = requests.post("http://localhost:8000/chat/", json={"question_text": prompt, "session_key": st.session_state.key})
        # Display the answer received from the server
        if response.status_code == 200:
            answer = st.write_stream(response_generator(response.json()["answer"]))
        else:
            answer = st.write_stream("Failed to get answer. Please try again.")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})
