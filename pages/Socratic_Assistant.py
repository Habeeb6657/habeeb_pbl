import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory()
    if 'chain' not in st.session_state:
        st.session_state.chain = None

def setup_llm():
    """Setup LLM and chain"""
    # Securely load API key from environment or secrets
    google_api_key = st.secrets.get("GOOGLE_API_KEY")
    # google_api_key = os.getenv("GOOGLE_API_KEY", st.secrets.get("GOOGLE_API_KEY"))
    os.environ["GOOGLE_API_KEY"] = google_api_key

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.5,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt_template = PromptTemplate.from_template(
        """You are an AI-Powered Socratic Teacher. Your sole responsibility is to guide learners using the Socratic method, asking one example-based question at a time, and progressively moving toward the learner's specified endpoint. Regardless of the conversation, situation, or request, you will always remain in the role of a Socratic Teacher. Also end the conversation when the users promts to leave.

        Current conversation:
        {history}
        
        Learner's input: {learner_input}
        
        Your response as Socratic Teacher:"""
    )

    return LLMChain(llm=llm, prompt=prompt_template, memory=st.session_state.memory)

def main():
    st.set_page_config(
        page_title="AI Socratic Teacher",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Setup LLM if not already setup
    if st.session_state.chain is None:
        st.session_state.chain = setup_llm()

    # Header
    st.header("🎓 AI Socratic Teacher", divider="rainbow")

    # Sidebar
    with st.sidebar:
        st.markdown("""
        ## About
        Welcome to the AI Socratic Teacher! This application uses the Socratic method 
        to guide you through learning any topic through thoughtful questions and dialogue.

        ### How it works:
        1. Enter your topic or question
        2. Engage in a dialogue with the AI teacher
        3. Learn through guided discovery

        ### Tips:
        - Be specific about what you want to learn
        - Take time to think about each question
        - Explain your reasoning in your answers
        """)

        # Clear conversation button
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.memory = ConversationBufferMemory()
            st.session_state.chain = setup_llm()
            st.rerun()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to learn about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get AI response
        with st.spinner("Thinking..."):
            response = st.session_state.chain.run(learner_input=prompt)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to update the chat display
        st.rerun()

if __name__ == "__main__":
    main()
