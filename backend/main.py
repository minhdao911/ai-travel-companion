from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import uuid
from enum import Enum

# Import the LangGraph app and state
from graphs.recommendation import (
    recommendation_graph,
    TravelState,
    MessageItem as GraphMessageItem,
)

app = FastAPI(title="AI Travel Companion API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue's default dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for graph task states
recommendation_graph_tasks = {}


class TaskStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TravelInputRequest(BaseModel):
    user_input: str
    conversation_history: Optional[List[GraphMessageItem]] = []
    optional_details_asked: bool = False


class GraphTaskStatusResponse(BaseModel):
    status: TaskStatus
    data: Optional[TravelState] = None  # Return the whole final state
    error: Optional[str] = None


async def run_travel_graph(task_id: str, initial_state: TravelState):
    """Runs the travel planning graph asynchronously and updates the task status."""
    global recommendation_graph_tasks
    try:
        print(f"[Task {task_id}] Starting graph execution.")
        recommendation_graph_tasks[task_id]["status"] = "PROCESSING"

        # Invoke the graph
        final_state = await recommendation_graph.ainvoke(initial_state)

        print(f"[Task {task_id}] Graph execution completed.")
        recommendation_graph_tasks[task_id]["status"] = "COMPLETED"
        recommendation_graph_tasks[task_id]["data"] = final_state

        if final_state.get("assistant_message"):
            print(
                f"[Task {task_id}] Assistant message: {final_state['assistant_message']}"
            )
            recommendation_graph_tasks[task_id]["status"] = "COMPLETED"
            return

        # Check for errors within the final state and potentially mark as FAILED
        if final_state.get("error_message"):
            print(
                f"[Task {task_id}] Graph finished with error: {final_state['error_message']}"
            )
            recommendation_graph_tasks[task_id]["status"] = "FAILED"
            recommendation_graph_tasks[task_id]["error"] = final_state["error_message"]
            return

    except Exception as e:
        print(f"[Task {task_id}] Critical error during graph execution: {str(e)}")
        recommendation_graph_tasks[task_id]["status"] = "FAILED"
        recommendation_graph_tasks[task_id]["error"] = str(e)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}


@app.post("/api/travel-recommendation")
async def plan_travel(request: TravelInputRequest):
    """Initiates the travel planning process using LangGraph."""
    global recommendation_graph_tasks
    try:
        task_id = str(uuid.uuid4())
        print(f"Received travel plan request, assigning Task ID: {task_id}")

        # Prepare initial state for the graph
        initial_state = TravelState(
            conversation_history=[
                {"role": x["role"], "content": x["content"]}
                for x in request.conversation_history
            ],
            user_input=request.user_input,
            optional_details_asked=request.optional_details_asked,
        )

        # Store initial task status
        recommendation_graph_tasks[task_id] = {
            "status": "PENDING",
            "data": None,
            "error": None,
        }

        # Start the graph execution in the background
        # Using asyncio.create_task for simplicity
        asyncio.create_task(run_travel_graph(task_id, initial_state))

        return {"task_id": task_id, "status": "PENDING"}

    except Exception as e:
        print(f"Error initiating travel plan task: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start planning task: {str(e)}"
        )


@app.get(
    "/api/travel-recommendation/status/{task_id}",
    response_model=GraphTaskStatusResponse,
)
async def get_plan_travel_status(task_id: str):
    """Gets the status and result of a travel planning task."""
    task_info = recommendation_graph_tasks.get(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")

    return GraphTaskStatusResponse(**task_info)
