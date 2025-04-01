from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Travel Companion API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue's default dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/destinations")
async def get_destinations():
    # Dummy data for testing
    return {
        "destinations": [
            {"id": 1, "name": "Paris", "country": "France", "description": "The City of Light"},
            {"id": 2, "name": "Tokyo", "country": "Japan", "description": "A blend of traditional and ultramodern"},
            {"id": 3, "name": "New York", "country": "USA", "description": "The Big Apple"},
        ]
    } 