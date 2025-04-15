from typing import TypedDict, List, Dict, Any, Optional
from travel.travel_details import get_travel_details
from scrapers.flight_scraper import (
    FlightScraper,
    to_markdown as to_markdown_flight,
)
from scrapers.hotel_scraper import (
    get_hotel_details,
    to_markdown as to_markdown_hotel,
)
from ai.models import model
from travel.prompts import get_travel_summary_prompt


# Define a structure for the search results consistent with the graph state
class SearchResult(TypedDict):
    raw_data: str
    json_data: Dict[str, Any]


def extract_travel_details_service(
    conversation_history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Extracts structured travel details from conversation history.

    Args:
        conversation_history: A list of message dictionaries (e.g., [{'role': 'user', 'content': '...'}, ...]).

    Returns:
        A dictionary containing the extracted travel preferences.

    Raises:
        ValueError: If details cannot be extracted or parsed.
    """
    try:
        # Format the conversation for the model
        # (Consider moving formatting logic here if needed)
        formatted_conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation_history]
        )

        # Call the existing LLM-based extraction function
        travel_details = get_travel_details(formatted_conversation)

        if not travel_details:
            raise ValueError("Failed to extract travel details from conversation.")

        print(f"--- Extracted Details: {travel_details}")
        return travel_details

    except Exception as e:
        print(f"Error in extract_travel_details_service: {str(e)}")
        # Re-raise as a specific error type or a generic one
        raise ValueError(f"Error extracting travel details: {e}")


async def search_flights_service(
    origin_airport_code: str,
    destination_airport_code: str,
    start_date: str,
    end_date: str,
    num_guests: int,
    preferences: Optional[Dict[str, Any]] = None,
) -> SearchResult:
    """
    Searches for flights based on provided details.

    Args:
        origin_airport_code: The IATA code of the origin airport.
        destination_airport_code: The IATA code of the destination airport.
        start_date: Departure date (YYYY-MM-DD).
        end_date: Return date (YYYY-MM-DD).
        num_guests: Number of travelers.
        preferences: Dictionary of flight preferences (e.g., {'class': 'economy', 'direct': False}).

    Returns:
        A SearchResult dictionary containing raw markdown and JSON flight data.

    Raises:
        Exception: If flight scraping or processing fails.
    """
    print(
        f"--- Starting Flight Search: {origin_airport_code} -> {destination_airport_code} ({start_date} - {end_date}) for {num_guests} guest(s)"
    )
    try:
        # Process preferences with defaults
        flight_prefs = {
            "seat_class": (
                preferences.get("class", "economy") if preferences else "economy"
            ),
            "direct": preferences.get("direct", False) if preferences else False,
        }

        scraper = FlightScraper(
            origin_airport_code=origin_airport_code,
            destination_airport_code=destination_airport_code,
            num_guests=num_guests,
            preferences=flight_prefs,  # Pass processed preferences
        )

        outbound = scraper.get_flight_details(start_date)
        if not outbound:
            raise Exception("Failed to get outbound flight details")

        inbound = scraper.get_flight_details(end_date)
        if not inbound:
            raise Exception("Failed to get inbound flight details")

        # Format results
        raw_results = f"### Outbound Flights ({start_date}):\n\n"
        raw_results += to_markdown_flight(outbound)
        raw_results += f"\n\n### Return Flights ({end_date}):\n\n"
        raw_results += to_markdown_flight(inbound)

        json_results = {"outbound": outbound, "inbound": inbound}

        print("--- Flight Search Completed Successfully")
        return {"raw_data": raw_results, "json_data": json_results}

    except Exception as e:
        print(f"Error in search_flights_service: {str(e)}")
        # Propagate the error for the graph to handle
        raise Exception(f"Flight search failed: {e}")


async def search_hotels_service(
    destination_city_name: str,
    start_date: str,
    end_date: str,
    num_guests: int,
    currency: Optional[str] = "USD",
    accommodation_types: Optional[List[str]] = ["hotel"],
) -> SearchResult:
    """
    Searches for hotels based on provided details.

    Args:
        destination_city_name: The name of the destination city.
        start_date: Check-in date (YYYY-MM-DD).
        end_date: Check-out date (YYYY-MM-DD).
        num_guests: Number of guests.
        currency: Currency code (e.g., "USD").
        accommodation_types: List of accommodation types to search for (e.g., ["hotel", "hostel"]).

    Returns:
        A SearchResult dictionary containing raw markdown and JSON hotel data.

    Raises:
        Exception: If hotel scraping or processing fails.
    """
    print(
        f"--- Starting Hotel Search: {destination_city_name} ({start_date} - {end_date}) for {num_guests} guest(s)"
    )
    try:
        # Prepare parameters for the scraper function
        params = {
            "location": destination_city_name,
            "checkin_date": start_date,
            "checkout_date": end_date,
            "num_guests": num_guests,
            "currency": currency,
            "accommodation_types": accommodation_types,
        }

        hotel_details = get_hotel_details(**params)
        if not hotel_details:
            raise Exception("Failed to get hotel details (returned empty)")

        # Format results
        raw_results = to_markdown_hotel(hotel_details)
        json_results = (
            hotel_details  # Assuming the function returns the desired JSON structure
        )

        print("--- Hotel Search Completed Successfully")
        return {"raw_data": raw_results, "json_data": json_results}

    except Exception as e:
        print(f"Error in search_hotels_service: {str(e)}")
        # Propagate the error for the graph to handle
        raise Exception(f"Hotel search failed: {e}")


def get_travel_summary(flights: str, hotels: str, **kwargs) -> str:
    prompt = get_travel_summary_prompt(flights, hotels, **kwargs)
    try:
        return model.invoke(prompt).content
    except Exception as e:
        print(f"Error getting travel summary: {str(e)}")
        raise SystemError(f"Error getting travel summary: {e}")
