import datetime
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from ..tools import Tools
from llm import DefaultModel
from aire.models.chat import *
from langchain_core.pydantic_v1 import BaseModel, validator, ValidationError
from aire.services.memory import post_event

tool_node = ToolNode(Tools)
llm = DefaultModel(temperature=0.0).bind_tools(Tools)
memory = MemorySaver()

# class EventState(BaseModel):
#     subject: str
#     date: datetime
#     ctx: AireChatContext
#     messages: list[AnyMessage]

    # @validator('date')
    # def validate_date(cls, value):
    #     if value < datetime.now():
    #         raise ValueError("Date is in the past")
    #     return value

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def tool_calling_llm(state: MessagesState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def add_event_to_memory(state: MessagesState):
    post_event(state.date, state.subject, state.ctx)
    return True

workflow = StateGraph(MessagesState)
workflow.add_node("tool_calling_llm", tool_calling_llm)
workflow.add_node("tools", ToolNode(Tools))

workflow.add_edge(START, "tool_calling_llm")

workflow.add_conditional_edges(
    "tool_calling_llm",
    tools_condition
)

workflow.add_edge("tools", END)

checkpointer = MemorySaver()

EventAgent = workflow.compile(checkpointer=checkpointer)