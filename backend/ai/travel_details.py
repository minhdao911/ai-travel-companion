from ai.models import model
from ai.travel_schemas import travel_preferences_schema
from utils.datetime import format_date

user_input_model = model.with_structured_output(travel_preferences_schema)

def get_travel_details(input: str) -> dict:
    prompt = f"""
        Read the following information from the user and extract the data into the structured output fields.
        
        The input is a conversation between a user and an AI assistant. When extracting information, 
        consider the context of questions and answers. For example, if the assistant asks
        "How many people are traveling?" and the user responds "1", understand that "1" refers to the 
        number of guests.

        IMPORTANT: 
        - DO NOT make any assumptions about travel details that the user has not explicitly provided
        - Only fill in fields where the user has clearly stated the information
        - Leave fields EMPTY if the user hasn't provided the specific information
        - If the user mentions origin or destination city, use the nearest airport code
        - If the user don't provide the number of guests, don't assume it's 1
        
        Conversation:
        {input}
        
        When providing dates give the format like this: May 2, 2025
        When providing airport codes give 3 uppercase letters.
        Make sure the airport code is valid.
    """
    try:
        return user_input_model.invoke(prompt)
    except Exception as e:
        print(f"Error in get_travel_details: {str(e)}")
        raise ValueError(f"Error parsing user input: {e}")

def check_missing_information(travel_details: dict) -> dict:
    """
    Check if any required information is missing and return a response
    with details about what information is missing.
    """
    missing_fields = []
    
    # Check for required fields
    if not travel_details.get('origin_airport_code'):
        missing_fields.append("origin_airport_code")
    
    if not travel_details.get('destination_airport_code'):
        missing_fields.append("destination_airport_code")
        
    if not travel_details.get('destination_city_name'):
        missing_fields.append("destination_city_name")
        
    if not travel_details.get('start_date'):
        missing_fields.append("start_date")
        
    if not travel_details.get('end_date'):
        missing_fields.append("end_date")
        
    if not travel_details.get('num_guests'):
        missing_fields.append("num_guests")
    
    if missing_fields:
        return {
            "complete": False,
            "missing_fields": missing_fields,
            "message": f"Please provide the following information: {', '.join(missing_fields)}."
        }
    
    return {
        "complete": True,
        "travel_details": travel_details
    }

def summarize_travel_details(travel_details: dict) -> dict:
    """
    Create a summary of the complete travel details.
    """
    return {
        "From": travel_details['origin_airport_code'],
        "To": travel_details['destination_airport_code'],
        "Destination": travel_details['destination_city_name'],
        "Guests": travel_details['num_guests'],
        "Departure": format_date(travel_details['start_date']),
        "Return": format_date(travel_details['end_date']),
        "Budget": f"${travel_details['budget']}" if travel_details['budget'] else "Not specified",
    }

def generate_conversation_response(conversation_history: list = []) -> dict:
    """
    Generate a conversational response based on user input and conversation history.
    This handles the complete chat flow including missing information and summaries.
    """
    try:
        # Format the conversation for the model to better understand context
        formatted_conversation = ""
        for message in conversation_history:
            role = "Assistant" if message.role == "assistant" else "User"
            formatted_conversation += f"{role}: {message.content}\n"
            
        # Extract travel details from formatted conversation
        travel_details = get_travel_details(formatted_conversation)
        
        # Check if we have all the required information
        check_result = check_missing_information(travel_details)
        
        if not check_result["complete"]:
            # Missing information - generate a friendly conversational response
            missing_fields = check_result["missing_fields"]
            response_templates = {
                "origin_airport_code": "I'll need to know where you're departing from. Could you please provide the airport code or city you'll be traveling from?",
                "destination_airport_code": "Which airport are you flying to? If you're not sure of the code, just let me know the city.",
                "destination_city_name": "What city are you planning to visit?",
                "start_date": "When are you planning to depart? (e.g., May 2, 2025)",
                "end_date": "And when will you be returning?",
                "num_guests": "How many people in total will be traveling?",
            }
            
            # Create a conversational response for missing information
            if len(missing_fields) == 1:
                # Only one field is missing
                field = missing_fields[0]
                message = f"Thanks for your travel request! {response_templates.get(field, f'Could you please provide the {field}?')}"
            else:
                # Multiple fields missing
                message = "Thanks for your travel request! I need a few more details to help you plan your trip:\n\n"
                for field in missing_fields[:3]:  # Limit to first 3 missing fields to avoid overwhelming the user
                    message += f"• {response_templates.get(field, f'Could you please provide the {field}?')}\n"
                
                if len(missing_fields) > 3:
                    message += f"\nWe'll fill in the other details after that."
            
            return {
                "complete": False,
                "message": message,
                "missing_fields": missing_fields
            }
        else:            
            # Create a conversational summary response
            message = f"Perfect! I've got all the details for your trip to {travel_details['destination_city_name']}. Here's a summary:\n\n"
            message += f"• Traveling from {travel_details['origin_airport_code']} to {travel_details['destination_airport_code']}\n"
            message += f"• {travel_details['num_guests']} traveler{'s' if travel_details['num_guests'] > 1 else ''}\n"
            message += f"• Departing on {format_date(travel_details['start_date'])}\n"
            message += f"• Returning on {format_date(travel_details['end_date'])}\n"
            message += f"• Budget: {f"${travel_details['budget']}" if travel_details['budget'] else "Not specified"}\n\n"
            message += "I can now help you find the best flights and accommodations for your trip."
            
            return {
                "complete": True,
                "message": message,
                "summary": summarize_travel_details(travel_details),
                "travel_details": travel_details
            }
    
    except Exception as e:
        # Handle errors with a friendly message
        print("Error while generating conversation response: ", e)
        return {
            "complete": False,
            "message": f"I'm sorry, I couldn't process your travel request properly. I need clear information about your departure city, destination, dates, and number of travelers. Please provide only the information you're sure about, and I'll ask for any missing details.",
            "error": str(e)
        }