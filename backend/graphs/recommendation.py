from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, END

from services.recommnendation import (
    extract_travel_details_service,
    search_flights_service,
    search_hotels_service,
    get_travel_summary,
)
from utils.format import format_nested_dict_for_prompt


# Define the structure for conversation history items if not already globally defined
# Reusing the definition from main.py for consistency
class MessageItem(TypedDict):
    role: str
    content: str


# Define the state for our travel planning graph
class TravelState(TypedDict, total=False):
    """Represents the state of our graph.

    Attributes:
        conversation_history: The history of the conversation.
        user_input: The latest user query.
        extracted_details: Details extracted from the conversation (destination, dates, etc.).
        flight_search_results: Results from the flight search API call.
        hotel_search_results: Results from the hotel search API call.
        final_summary: The final generated travel plan summary.
        error_message: Any critical error message encountered during the flow.
        search_attempt_count: Optional counter for retries.
        assistant_message: Message to ask the user for missing info
        optional_details_asked: Flag to track if optional info was requested
    """

    conversation_history: List[MessageItem]
    user_input: str
    extracted_details: Optional[Dict[str, Any]]
    flight_search_results: Optional[
        Dict[str, Any]
    ]  # Structure to hold {'raw_data': str, 'json_data': dict}
    hotel_search_results: Optional[
        Dict[str, Any]
    ]  # Structure to hold {'raw_data': str, 'json_data': dict}
    final_summary: Optional[str]
    error_message: Optional[str]
    assistant_message: Optional[str]
    optional_details_asked: bool = False
    # search_attempt_count: int # Uncomment if implementing retries


# --- Graph Nodes --- #


def extract_details_node(state: TravelState) -> Dict[str, Any]:
    """Extracts travel details, asking for clarification if necessary."""
    print("--- Node: Extracting Details ---")
    conversation_history = state["conversation_history"]
    user_input = state["user_input"]

    try:
        extracted_details = extract_travel_details_service(conversation_history)
        optional_details_asked = state.get(
            "optional_details_asked", False
        )  # Get flag from state

        # --- Check for Missing Required Information --- #
        required_keys = [
            "origin_airport_code",
            "destination_airport_code",
            "destination_city_name",
            "start_date",
            "end_date",
            "num_guests",
        ]
        missing_fields = [
            key
            for key in required_keys
            if key not in extracted_details or not extracted_details[key]
        ]

        if missing_fields:
            print(f"Extraction Incomplete: Missing required keys - {missing_fields}")

            # Use templates to formulate the question
            response_templates = {
                "origin_airport_code": "Could you please provide the airport code or city you'll be traveling from?",
                "destination_airport_code": "Which airport are you flying to? If you're not sure of the code, just let me know the city.",
                "destination_city_name": "What city are you planning to visit?",
                "start_date": "When are you planning to depart? (e.g., YYYY-MM-DD)",
                "end_date": "And when will you be returning? (e.g., YYYY-MM-DD)",
                "num_guests": "How many people in total will be traveling?",
            }

            if len(missing_fields) == 1:
                field = missing_fields[0]
                message = f"Thanks! To continue planning, {response_templates.get(field, f'could you please provide the {field}?')}"
            else:
                message = (
                    "Thanks! I need a few more details to help you plan your trip:\n\n"
                )
                for field in missing_fields[:3]:  # Ask for up to 3 at a time
                    message += f"* {response_templates.get(field, f'Could you please provide the {field}?')}\n"
                if len(missing_fields) > 3:
                    message += (
                        f"\nLet's start with those, and we can fill in the rest after."
                    )

            # Return the assistant message to pause and ask the user
            return {"assistant_message": message}

        # --- Required Fields Present - Check Optional Fields (if not already asked) --- #
        if not optional_details_asked:
            print("Checking for optional details (first pass).")
            optional_missing = []
            # Define optional fields/structures to check
            if not extracted_details.get("budget"):
                optional_missing.append("budget")
            flight_prefs = extracted_details.get("flight", {})
            if not flight_prefs.get("class") and not flight_prefs.get("direct"):
                optional_missing.append("flight_prefs")
            acc_prefs = extracted_details.get("accommodation", {})
            if not acc_prefs.get("type") and not acc_prefs.get(
                "amenities"
            ):  # Simplified check
                optional_missing.append("accommodation_prefs")

            if optional_missing:
                print(f"Optional fields missing: {optional_missing}")
                # Formulate message asking for optional details
                opt_templates = {
                    "budget": "your budget",
                    "flight_prefs": "flight preferences (e.g., class, direct)",
                    "accommodation_prefs": "accommodation preferences (e.g., type, amenities)",
                }
                ask_for = ", ".join([opt_templates.get(f, f) for f in optional_missing])
                message = f"Great, I have the main details! To help find the best options, you can also tell me about {ask_for}. Or, just say 'continue' and I'll use defaults."

                # Return message and set flag to True
                return {"assistant_message": message, "optional_details_asked": True}
            else:
                # All optional fields checked are present, mark as asked and proceed
                print("Optional fields present or not applicable.")
                return {
                    "extracted_details": extracted_details,
                    "user_input": user_input,
                    "optional_details_asked": True,  # Mark as asked
                }
        else:
            # Already asked for optional details, proceed regardless
            print("Optional details already asked. Proceeding with extracted details.")
            return {"extracted_details": extracted_details, "user_input": user_input}

    except Exception as e:
        print(f"Error in extract_details_node: {e}")
        # Return critical error to stop the flow
        return {
            "error_message": f"Sorry, I encountered an error trying to understand your request: {str(e)}"
        }


async def search_flights_node(state: TravelState) -> Dict[str, Any]:
    """Searches for flights based on extracted details."""
    print("--- Node: Searching Flights ---")
    error_message = state.get("error_message")
    if error_message:
        print("Skipping flight search due to previous error.")
        return {}

    extracted_details = state.get("extracted_details")
    if not extracted_details:
        return {
            "error_message": "Cannot search flights: Extracted details are missing."
        }

    try:
        # Ensure all required arguments are present
        origin = extracted_details.get("origin_airport_code")
        destination = extracted_details.get("destination_airport_code")
        start_date = extracted_details.get("start_date")
        end_date = extracted_details.get("end_date")
        num_guests = extracted_details.get("num_guests")
        preferences = extracted_details.get("preferences", {}).get(
            "flight"
        )  # Extract flight-specific prefs

        if not all([origin, destination, start_date, end_date, num_guests]):
            missing = [
                k
                for k, v in {
                    "origin_airport_code": origin,
                    "destination_airport_code": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_guests": num_guests,
                }.items()
                if not v
            ]
            print(f"Flight Search Error: Missing required args - {missing}")
            # Don't set a graph-level error, just return empty results for this node
            return {
                "flight_search_results": {"error": f"Missing required args: {missing}"}
            }

        results = await search_flights_service(
            origin_airport_code=origin,
            destination_airport_code=destination,
            start_date=start_date,
            end_date=end_date,
            num_guests=num_guests,
            preferences=preferences,
        )
        return {"flight_search_results": results}
    except Exception as e:
        print(f"Error in search_flights_node: {e}")
        # Store error within the results for this specific search
        return {"error_message": f"Flight search failed: {str(e)}"}


async def search_hotels_node(state: TravelState) -> Dict[str, Any]:
    """Searches for hotels based on extracted details."""
    print("--- Node: Searching Hotels ---")
    error_message = state.get("error_message")
    if error_message:
        print("Skipping hotel search due to previous error.")
        return {}

    extracted_details = state.get("extracted_details")
    if not extracted_details:
        return {"error_message": "Cannot search hotels: Extracted details are missing."}

    try:
        # Ensure all required arguments are present
        destination = extracted_details.get("destination_city_name")
        start_date = extracted_details.get("start_date")
        end_date = extracted_details.get("end_date")
        num_guests = extracted_details.get("num_guests")
        currency = extracted_details.get(
            "currency", "EUR"
        )  # Default currency if not specified
        # Get accommodation type preferences with fallback to ["hotel"]
        preferences = extracted_details.get("preferences", {})
        accommodation = preferences.get("accommodation", {})
        accommodation_types = accommodation.get("type", ["hotel"])

        if not all([destination, start_date, end_date, num_guests]):
            missing = [
                k
                for k, v in {
                    "destination_city_name": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_guests": num_guests,
                }.items()
                if not v
            ]
            print(f"Hotel Search Error: Missing required args - {missing}")
            return {
                "hotel_search_results": {"error": f"Missing required args: {missing}"}
            }

        results = await search_hotels_service(
            destination_city_name=destination,
            start_date=start_date,
            end_date=end_date,
            num_guests=num_guests,
            currency=currency,
            accommodation_types=accommodation_types,
        )
        return {"hotel_search_results": results}
    except Exception as e:
        print(f"Error in search_hotels_node: {e}")
        return {"error_message": f"Hotel search failed: {str(e)}"}


def generate_summary_node(state: TravelState) -> Dict[str, Any]:
    """Generates a final summary based on search results."""
    print("--- Node: Generating Summary ---")
    error_message = state.get("error_message")
    if error_message:
        print("Skipping summary generation due to previous error.")
        # Optionally generate a summary indicating the error
        # return {"final_summary": f"Could not complete planning due to an error: {error_message}"}
        return {}

    extracted_details = state.get("extracted_details")
    flight_results = state.get("flight_search_results")
    hotel_results = state.get("hotel_search_results")

    if not extracted_details:
        return {
            "error_message": "Cannot generate summary: Extracted details are missing."
        }

    # Prepare inputs for the summary function, handling potential errors/missing data
    flights_str = (
        flight_results.get("raw_data", "Flight search data not available.")
        if flight_results
        else "Flight search data not available."
    )
    hotels_str = (
        hotel_results.get("raw_data", "Hotel search data not available.")
        if hotel_results
        else "Hotel search data not available."
    )

    # Include error messages in the summary input if searches failed
    if flight_results and flight_results.get("error"):
        flights_str += f"\n\n*Note: Encountered an error during flight search: {flight_results['error']}*"
    if hotel_results and hotel_results.get("error"):
        hotels_str += f"\n\n*Note: Encountered an error during hotel search: {hotel_results['error']}*"

    # Prepare kwargs for the summary function
    summary_kwargs = {
        "start_date": extracted_details.get("start_date"),
        "end_date": extracted_details.get("end_date"),
        "num_guests": extracted_details.get("num_guests"),
        "preferences": format_nested_dict_for_prompt(
            extracted_details.get("preferences", {})
        ),
        # Add any other relevant details from extracted_details
        "origin": extracted_details.get("origin_city_name")
        or extracted_details.get("origin_airport_code"),
        "destination": extracted_details.get("destination_city_name"),
    }
    # Filter out None values from kwargs
    summary_kwargs = {k: v for k, v in summary_kwargs.items() if v is not None}

    try:
        summary = get_travel_summary(flights_str, hotels_str, **summary_kwargs)
        print("--- Summary Generated Successfully ---")
        return {"final_summary": summary}
    except Exception as e:
        print(f"Error in generate_summary_node: {e}")
        return {"error_message": f"Failed to generate travel summary: {str(e)}"}


# --- Graph Definition --- #


# Define the conditional edge logic
def should_continue(state: TravelState) -> str:
    """Determines the next step after detail extraction."""
    print("--- Condition: Checking Extraction Results ---")
    if state.get("error_message"):
        print("Critical error encountered. Ending flow.")
        return "end_flow_error"
    if state.get("assistant_message"):
        print("Missing information. Asking user.")
        return "ask_user"  # New path: Need to ask user for info
    if state.get("extracted_details"):
        print("Extraction successful and complete. Proceeding to parallel search.")
        return "continue_to_search"
    else:
        # Fallback in case state is somehow unclear after extraction
        print("Extraction state unclear. Ending flow as fallback.")
        return "end_flow_error"


# Build the graph
workflow = StateGraph(TravelState)

# Add nodes
workflow.add_node("extract_details", extract_details_node)
workflow.add_node("search_flights", search_flights_node)
workflow.add_node("search_hotels", search_hotels_node)
workflow.add_node("generate_summary", generate_summary_node)

# Set the entry point
workflow.set_entry_point("extract_details")

# Add conditional edges
workflow.add_conditional_edges(
    "extract_details",
    should_continue,
    {
        "continue_to_search": "search_flights",  # If complete, proceed to search
        "ask_user": END,  # If missing info, pause (END) and wait for user input
        "end_flow_error": END,  # If error, end
    },
)

# Add an *unconditional* edge from extract_details to the *other* parallel node.
# This edge is ONLY triggered if the condition maps to "continue_to_search".
workflow.add_edge("extract_details", "search_hotels")

# Edges after searches complete
workflow.add_edge("search_flights", "generate_summary")
workflow.add_edge("search_hotels", "generate_summary")

# The summary node is the final step before ending normally
workflow.add_edge("generate_summary", END)

# Compile the graph
recommendation_graph = workflow.compile()

print("--- Travel Plan Graph Compiled ---")
