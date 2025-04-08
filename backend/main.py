from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from travel.travel_details import generate_conversation_response, get_travel_summary
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from scrapers.flight_scraper import get_flight_search_url, scrape_flights
from scrapers.hotel_scraper import get_hotel_search_url, scrape_hotels
from tasks import TaskManager, TaskStatus
import threading

app = FastAPI(title="AI Travel Companion API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue's default dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_manager = TaskManager()

class MessageItem(BaseModel):
    role: str
    content: str

class TravelInputRequest(BaseModel):
    user_input: str
    conversation_history: Optional[List[MessageItem]] = []

class BaseSearchRequest(BaseModel):
    destination_city_name: str
    start_date: str
    end_date: str
    num_guests: int
    budget: Optional[int] = None
    preferences: Optional[str] = None

class FlightSearchRequest(BaseSearchRequest):
    origin_city_name: str

class TravelSummaryRequest(BaseSearchRequest):
    flight_results: str
    hotel_results: str

def run_async(coro):
    """Helper function to run async code"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def process_flights_search(task_id, origin, destination, start_date, end_date, num_guests):
    try:
        # Update task status to processing
        task_manager.update_task_status(task_id, TaskStatus.PROCESSING)

        # Get flight search url
        url = run_async(get_flight_search_url(origin, destination, start_date, end_date, num_guests))
        if not url:
            raise Exception("Failed to get flight search url")
                
        # Scrape flights
        flight_results = run_async(scrape_flights(url))
        print("--- Flight results ---")
        print(flight_results)
        if not flight_results:
            raise Exception("Failed to scrape flights")
        
        # Update task status to completed
        task_manager.update_task_status(task_id, TaskStatus.COMPLETED, data=flight_results)
    except Exception as e:
        print(f"Error processing flights search: {str(e)}")
        task_manager.update_task_status(task_id, TaskStatus.FAILED, error=str(e))

def process_hotels_search(task_id, destination, start_date, end_date, num_guests):
    try:
        # Update task status to processing
        task_manager.update_task_status(task_id, TaskStatus.PROCESSING)

        # Get hotel search url
        url = run_async(get_hotel_search_url(destination, start_date, end_date, num_guests))
        if not url:
            raise Exception("Failed to get hotel search url")
        
        # Scrape hotels
        hotel_results = run_async(scrape_hotels(url))
        print("--- Hotel results ---")
        print(hotel_results)
        if not hotel_results:
            raise Exception("Failed to scrape hotels")
        
        # Update task status to completed
        task_manager.update_task_status(task_id, TaskStatus.COMPLETED, data=hotel_results)
    except Exception as e:
        print(f"Error processing hotels search: {str(e)}")
        task_manager.update_task_status(task_id, TaskStatus.FAILED, error=str(e))

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
    
@app.post("/api/travel-summary")
async def process_travel_summary(request: TravelSummaryRequest):
    try:
        # Generate a summary of the travel
        kwargs = {
            "start_date": request.start_date,
            "end_date": request.end_date,
            "num_guests": request.num_guests,
        }

        if hasattr(request, 'budget') and request.budget is not None:
            kwargs['budget'] = request.budget

        if hasattr(request, 'preferences') and request.preferences is not None:
            kwargs['preferences'] = request.preferences
            
        result = get_travel_summary(
            request.flight_results,
            request.hotel_results,
            **kwargs
        )   
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a task"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "status": task.status,
        "data": task.data,
        "error": task.error
    }

@app.post("/api/search-flights")
def search_flights(request: FlightSearchRequest):
    try:
        # Store the task in the task manager
        task_id = task_manager.add_task()

        # Extract flight details from the request
        origin_city_name = request.origin_city_name
        destination_city_name = request.destination_city_name
        start_date = request.start_date
        end_date = request.end_date
        num_guests = request.num_guests

        if not all([origin_city_name, destination_city_name, start_date, end_date, num_guests]):
            task_manager.update_task_status(task_id, TaskStatus.FAILED, error="Missing required flight details")
            raise HTTPException(status_code=400, detail="Missing required flight details")

        # Start background thread
        thread = threading.Thread(
            target=process_flights_search, 
            args=(task_id, origin_city_name, destination_city_name, start_date, end_date, num_guests), 
            daemon=True
        )
        thread.start()

        return {"task_id": task_id, "status": TaskStatus.PENDING}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/search-hotels")
def search_hotels(request: BaseSearchRequest):
    try:
        # Store the task in the task manager
        task_id = task_manager.add_task()

        # Extract hotel details from the request
        destination_city_name = request.destination_city_name
        start_date = request.start_date
        end_date = request.end_date
        num_guests = request.num_guests

        if not all([destination_city_name, start_date, end_date, num_guests]):
            task_manager.update_task_status(task_id, TaskStatus.FAILED, error="Missing required hotel details")
            raise HTTPException(status_code=400, detail="Missing required hotel details")

        # Start background thread
        thread = threading.Thread(
            target=process_hotels_search, 
            args=(task_id, destination_city_name, start_date, end_date, num_guests), 
            daemon=True
        )
        thread.start()

        return {"task_id": task_id, "status": TaskStatus.PENDING}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
