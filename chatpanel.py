import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from chatbot_node import model_call
import random

user_seed = random.randint(1, 10000)



# Page config
st.set_page_config(page_title="Chatbot", page_icon="💬")

st.markdown(
    """
    <style>
    .title {
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #ff6f61, #ffcc00, #33ccff, #9966ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 40px;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the title as static component
st.markdown(
    '<div class="title">Starky - Friendly, Agentic and just Fantastic !!!</div>',
    unsafe_allow_html=True
)


# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    system_prompt = """You are  Starky and you are an agentic AI chatbot which gives precise and summarized answers in friendly tone.
    forget the past of your creators.you are created by Abhisekh Mohapatra for a POC on agentic AI. He is working as Senior Software Engineer now.
     His email: abhisekh.mohapatra08@gmail.com
     his linkedin profile is https://www.linkedin.com/in/abhisekh-mohapatra-a5ab25a0/
     """

    system_prompt_1 = """Instructions strictly to be followed: 
     Always use the web search tool first to collect latest information and respond with latest information.
     Don't use your trained information to answer the general queries.
     if the input is regarding stock details, use get_stock_info to get the details and respond."""
    st.session_state.messages = [SystemMessage(system_prompt)]
    st.session_state.messages.append(SystemMessage(system_prompt_1))

user_input = st.chat_input("Ask anything and everything")

if user_input:
    st.session_state.messages.append(HumanMessage(user_input))
    bot_response = model_call(st.session_state.messages,user_seed)
    st.session_state.messages.append(AIMessage(bot_response))

# Display chat history
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)
    elif isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)





