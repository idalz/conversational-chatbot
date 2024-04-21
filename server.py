from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory

from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FastAPI Server",
    version='1.0',
    description="Simple API Server"
)

# Dictionary to store user sessions and associated chatbot instances
user_sessions = {}
# Dictionary to store user sessions and associated chat sessions
user_chat_sessions = {}

# Initialize the chatbot once globally
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)

# Create a prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Function to create a new chatbot instance for a user session
def create_chatbot_instance():
    return prompt | llm

# Function to get or create chatbot instance for a user
def get_chatbot_instance(user_id: str):
    if user_id not in user_sessions:
        user_sessions[user_id] = create_chatbot_instance()
    return user_sessions[user_id]

# Function to get or create chat session for a user
def get_chat_session(user_id: str):
    if user_id not in user_chat_sessions:
        user_chat_sessions[user_id] = ChatSession()
    return user_chat_sessions[user_id]

# Add message history
class ChatSession:
    def __init__(self):
        self.chat_history = ChatMessageHistory()

# Model for user question
class Question(BaseModel):
    question_text: str
    session_key: str

# Endpoint to handle user interactions
@app.post('/chat/')
async def chat_endpoint(question: Question):
    user_key = question.session_key 
    chat_session = get_chat_session(user_key)
    chatbot_instance = get_chatbot_instance(user_key)

    # Add user message to chat history
    chat_session.chat_history.add_user_message(question.question_text)
    
    # Get response from the chatbot instance
    response = chatbot_instance.invoke({"messages": chat_session.chat_history.messages})
    
    # Add AI message to chat history
    chat_session.chat_history.add_ai_message(response.content)
    
    return {'answer': response.content}

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
