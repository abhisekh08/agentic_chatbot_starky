import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from chatbot_node import model_call



# Page config
st.set_page_config(page_title="Chatbot", page_icon="💬")

st.title("Starky - Friendly,Agentic and just Fantastic !!!")


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
    bot_response = model_call(st.session_state.messages)
    st.session_state.messages.append(AIMessage(bot_response))

# Display chat history
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)
    elif isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)





