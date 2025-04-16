from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import json
from starlette.responses import StreamingResponse
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    BaseMessage,
)
from ai.summary import get_summary
from ai.assistant import (
    graph as assistant_graph,
)

app = FastAPI(title="AI Travel Companion API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StreamRequest(BaseModel):
    messages: List[Dict[str, Any]]


class SummaryRequest(BaseModel):
    user_input: str


def _convert_message_dicts_to_objects(
    messages: List[Dict[str, Any]],
) -> List[BaseMessage]:
    """Converts message dictionaries from the request to LangChain message objects."""
    output_messages = []
    print(f"Converting message dicts: {messages}")
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        tool_calls = msg.get("tool_calls")
        tool_call_id = msg.get("tool_call_id")

        if not content and not tool_calls:
            if role == "assistant":
                pass
            else:
                print(f"Skipping message with empty content and no tool calls: {msg}")
                continue

        if role == "user":
            output_messages.append(HumanMessage(content=content or ""))
        elif role == "assistant":
            if tool_calls and isinstance(tool_calls, list):
                valid_tool_calls = []
                for tc in tool_calls:
                    if (
                        isinstance(tc, dict)
                        and tc.get("id")
                        and tc.get("name")
                        and isinstance(tc.get("args"), dict)
                    ):
                        valid_tool_calls.append(
                            {
                                "id": tc["id"],
                                "name": tc["name"],
                                "args": tc["args"],
                                "type": "tool_call",
                            }
                        )
                    else:
                        print(f"Warning: Invalid tool_call format skipped: {tc}")
                if valid_tool_calls:
                    output_messages.append(
                        AIMessage(content=content or "", tool_calls=valid_tool_calls)
                    )
                else:
                    output_messages.append(AIMessage(content=content or ""))

            else:
                output_messages.append(AIMessage(content=content or ""))
        elif role == "tool":
            if tool_call_id:
                output_messages.append(
                    ToolMessage(content=content or "", tool_call_id=tool_call_id)
                )
            else:
                print(f"Warning: Tool message missing tool_call_id: {msg}")
        else:
            print(f"Warning: Unrecognized message role '{role}' skipped: {msg}")

    print(f"Converted LangChain messages: {output_messages}")
    return output_messages


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}


@app.post("/api/chat/summary")
async def get_chat_summary(request: SummaryRequest):
    """Get a short summary of the user's input."""
    summary = get_summary(request.user_input)
    if summary:
        return {"summary": summary}
    else:
        raise HTTPException(status_code=500, detail="Failed to get chat summary")


@app.post("/api/chat/stream")
async def stream_chat(request: StreamRequest):
    """Streams responses for the recommendation assistant using Server-Sent Events."""
    thread_id = f"stream_{uuid.uuid4()}"
    print(f"Received stream request, assigning Thread ID: {thread_id}")

    try:
        graph_input = {"messages": _convert_message_dicts_to_objects(request.messages)}

        if not graph_input["messages"]:
            print(f"[Thread {thread_id}] No valid messages found after conversion.")

            async def empty_stream():
                yield f"data: {json.dumps({'type': 'error', 'message': 'No valid messages received.'})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"

            return StreamingResponse(empty_stream(), media_type="text/event-stream")

        async def event_stream():
            try:
                async for event in assistant_graph.astream_events(
                    graph_input,
                    config={"configurable": {"thread_id": thread_id}},
                    version="v1",
                ):
                    kind = event["event"]
                    data = event.get("data", {})
                    name = event.get("name", "")

                    if kind == "on_chat_model_stream":
                        chunk = data.get("chunk")
                        if chunk and chunk.content:
                            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                        if chunk and chunk.tool_call_chunks:
                            for tool_chunk in chunk.tool_call_chunks:
                                yield f"data: {json.dumps({'type': 'tool_call_chunk', 'chunk': tool_chunk})}\n\n"

                    elif kind == "on_tool_start":
                        print(
                            f"\n--\nStarting tool: {name} with inputs: {data.get('input')}\n--"
                        )
                        yield f"data: {json.dumps({'type': 'tool_start', 'name': name, 'input': data.get('input')})}\n\n"

                    elif kind == "on_tool_end":
                        print(
                            f"\n--\nEnded tool: {name}\nTool output was: {data.get('output')}\n--"
                        )
                        yield f"data: {json.dumps({'type': 'tool_end', 'name': name })}\n\n"

            except Exception as e:
                print(f"[Thread {thread_id}] Error during stream generation: {str(e)}")
                import traceback

                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'message': f'Stream error: {str(e)}'})}\n\n"
            finally:
                print(f"[Thread {thread_id}] Stream ended.")
                yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        print(f"Error initiating recommendation stream: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to start recommendation stream: {str(e)}"
        )
