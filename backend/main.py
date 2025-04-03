from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai.travel_details import generate_conversation_response
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AI Travel Companion API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue's default dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageItem(BaseModel):
    role: str
    content: str

class TravelInputRequest(BaseModel):
    user_input: str
    conversation_history: Optional[List[MessageItem]] = []

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

@app.post("/api/travel-details")
async def process_travel_details(request: TravelInputRequest):
    try:
        # Generate a response based on the conversation
        result = generate_conversation_response(
            request.conversation_history
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
