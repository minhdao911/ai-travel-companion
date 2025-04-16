from typing import TypedDict, Annotated
from datetime import datetime

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

from ai.models import llm
from tools.flight_scraper import search_flights
from tools.hotel_scraper import search_hotels
from utils.tools import create_tool_node_with_fallback


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State) -> State:
        while True:
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful flight and hotel search assistant that provides the best flight and hotel options for the user, and answers questions related to the flight and hotel search. "
            " You can not book flights or hotels, only search for them. "
            " Use the provided tools to search for flights and hotels. "
            " If there are some missing details required to search, ask the user for more information. "
            " When searching for hotels, you can make additional web search to find the best options or fill in missing details like amenities, location, etc. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

tools = [search_flights, search_hotels, DuckDuckGoSearchRun()]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)

builder = StateGraph(State)

builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# For testing the graph locally
if __name__ == "__main__":
    import asyncio
    from langchain_core.messages import HumanMessage

    async def run_interactive_test():
        config = {"configurable": {"thread_id": "test-thread-interactive"}}
        print("--- Starting Interactive Test ---")
        print("Enter 'quit' to exit.")

        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                print("Exiting interactive test.")
                break

            input_message = HumanMessage(content=user_input)

            print("Assistant: ", end="", flush=True)
            async for event in graph.astream_events(
                {"messages": [input_message]}, config=config, version="v1"
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        print(content, end="", flush=True)
                elif kind == "on_tool_start":
                    print(
                        f"\n--\nStarting tool: {event['name']} with inputs: {event['data'].get('input')}\n--",
                        flush=True,
                    )
                elif kind == "on_tool_end":
                    # Tool output is usually processed internally, you might not want to print it directly
                    # You can uncomment the lines below if you want to see the raw tool output
                    # print(f"\n--\nEnded tool: {event['name']}")
                    # print(f"Tool output was: {event['data'].get('output')}")
                    # print("--", flush=True)
                    pass  # Keep it cleaner for interactive use
                elif kind in {"on_chain_start", "on_chain_end"}:
                    pass  # Optional: print chain start/end events

            print()  # Newline after assistant response

    asyncio.run(run_interactive_test())
