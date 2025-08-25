import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from config import credentials

from langchain_groq import ChatGroq
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from agentic_tools import get_stock_info, search_query_from_web
from langgraph.prebuilt import ToolNode

# setup logs
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/web_agentic_chatbot_%Y-%m-%d.log")
logging.basicConfig(level=logging.INFO,
                    filename=log_filename,
                    format='%(asctime)s %(message)s',
                    filemode='w')
logging.info("Logging starts...")

# Load variables from .env into environment variables
load_dotenv()

# setup groq
GROQ_API_KEY = credentials["GROQ_API_KEY"]
APP_NAME = credentials["APP_NAME"]

# create llm
llm_base = ChatGroq(model_name=credentials["MODEL_NAME"],
                    temperature=0.3,
                    groq_api_key=GROQ_API_KEY,
                    reasoning_format="parsed")

# create tool
tools = [search_query_from_web, get_stock_info]

# bind tools
llm_with_tools = llm_base.bind_tools(tools)

# tool Node
tool_node = ToolNode(tools)

# create state
class State(dict):
    messages: Annotated[list, add_messages]

# chatbot node
def chatbot(state: State):
    print(state)
    return {"messages": [llm_with_tools.invoke(state["messages"]) ]}

# create_router
def router(state: State):
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return END

# Assemble Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_conditional_edges("chatbot", router)

# memory
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)


# model module
def model_call(messages):
    responses = graph.invoke({"messages": messages},
                             config={"configurable":{"thread_id": 1234}})
    return responses["messages"][-1].content









