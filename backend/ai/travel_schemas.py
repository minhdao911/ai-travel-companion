travel_preferences_schema = {
    "title": "TravelPlan",
    "description": "A schema for a travel plan including destination, dates, budget, accommodation, flight, activities, and food preferences.",
    "type": "object",
    "properties": {
        "origin_airport_code": {"type": "string", "description": "The 3-letter airport code for departure"},
        "destination_airport_code": {"type": "string", "description": "The 3-letter airport code for arrival"},
        "origin_city_name": {"type": "string", "description": "The name of the departure city"},
        "destination_city_name": {"type": "string", "description": "The name of the destination city"},
        "num_guests": {"type": "integer", "description": "Number of travelers"},
        "start_date": {"type": "string", "description": "Departure date in format like May 2, 2025"},
        "end_date": {"type": "string", "description": "Return date in format like May 9, 2025"},
        "budget": {"type": "integer", "description": "Total budget for the trip in USD"},
        "accommodation": {
            "type": "object",
            "description": "Accommodation preferences",
            "properties": {
                "type": {"type": "string", "description": "Type of accommodation (hotel, hostel, etc.)"},
                "max_price_per_night": {"type": "integer", "description": "Maximum price per night in USD"},
                "amenities": {
                    "type": "array",
                    "description": "List of desired amenities",
                    "items": {"type": "string"}
                }
            }
        },
        "flight": {
            "type": "object",
            "description": "Flight preferences",
            "properties": {
                "class": {"type": "string", "description": "Flight class (economy, business, first)"},
                "direct": {"type": "boolean", "description": "Whether direct flights are preferred"}
            }
        },
        "activities": {
            "type": "array",
            "description": "List of desired activities",
            "items": {"type": "string"}
        },
        "food_preferences": {
            "type": "array",
            "description": "List of food preferences",
            "items": {"type": "string"}
        }
    },
    "required": ["origin_city_name", "destination_city_name", "num_guests", "start_date", "end_date"]
}