def travel_preferences_prompt(input: str) -> str:
    return f"""
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
        
        When providing dates give the format like this: 2025-05-02
        When providing airport codes give 3 uppercase letters.
        Make sure the airport code is valid.
    """

def get_travel_summary_prompt(flights: str, hotels: str, **kwargs) -> str:
    # Suggestion: Calculate number_of_nights here based on start/end dates
    # num_nights = calculate_nights(kwargs.get('start_date'), kwargs.get('end_date'))
    # Then pass num_nights into the prompt if needed, or use it for pre-calculation.

    # Extract relevant preferences for clarity in the prompt
    start_date = kwargs.get('start_date', 'unknown start date')
    end_date = kwargs.get('end_date', 'unknown end date')
    num_guests = kwargs.get('num_guests', 'unknown number of guests')
    preferences = kwargs.get('preferences', "not specified")

    return f"""Summarize the provided flight and hotel options. Calculate the total estimated travel cost, including flights and the total hotel cost for the duration of the stay. Finally, provide a recommendation for one flight combination (outbound and return) and one hotel, along with a justification.

        Given Information:
        - Flights Details: {flights}
        - Hotels Details: {hotels} (Note: Hotel prices listed are typically per night)
        - Travel Dates: From {start_date} to {end_date}
        - Number of Guests: {num_guests}
        - User Preferences: {preferences} 
        
        Instructions:
        1.  Calculate Total Duration: Determine the number of nights for the hotel stay based on the start and end dates.
        2.  Calculate Total Cost: 
            - Sum the cost of the chosen outbound and return flights.
            - Calculate the total hotel cost (Price per night * Number of nights).
            - Sum the flight and hotel costs for the grand total.
        3.  Make Recommendations:
            - Select ONE outbound and ONE return flight combination AND ONE hotel.
            - If user preferences are provided: Base the recommendation strictly on matching those preferences ({preferences}). Consider factors like budget, airline choice, flight times, hotel rating, amenities, location preferences, etc., if mentioned.
            - If no specific preferences are provided:
                - Recommend the flight combination that offers a good balance between the lowest price and shortest travel time (including layovers).
                - Recommend the hotel that offers the best combination of high guest ratings, lowest price, and a generally desirable location (e.g., close to city center, attractions, or transport links).
        4.  Format the Output: Structure the response clearly using basic markdown as shown below. Ensure all requested sections are included.

        Output Structure:
        ## Flight and Hotel Recommendation:
        
        **Travel Summary:** [Origin City/Airport] to [Destination City/Airport] for [Number of Guests]
        **Dates:** {start_date} to {end_date} ([Calculated number] nights)

        ### Recommended Flight:
        Outbound:
        - Airline: [Airline Name]
        - Flight No.: [Flight Number]
        - Departure: [Departure Time] at [Departure Airport]
        - Arrival: [Arrival Time] at [Arrival Airport]
        - Duration: [Duration]
        - Price: [Price]
        Return:
        - Airline: [Airline Name]
        - Flight No.: [Flight Number]
        - Departure: [Departure Time] at [Departure Airport]
        - Arrival: [Arrival Time] at [Arrival Airport]
        - Duration: [Duration]
        - Price: [Price]
        **Total Flight Cost:** [Calculated total flight cost]

        ### Recommended Hotel:
        - Name: [Hotel Name]
        - Rating: [Rating]/5
        - Price per night: [Price]
        - Location: [Location Info]
        - Amenities: [Amenities]
        **Total Hotel Cost:** [Calculated total hotel cost for the duration]

        **Estimated Total Trip Cost:** [Grand total of flights + hotel]

        ---
        [Explain *why* this specific flight combination and hotel were chosen. Refer back to the user's preferences (e.g., "This flight is the cheapest direct option within your preferred departure time window.") or the default criteria (e.g., "This hotel has the highest rating below your budget and is centrally located.")]
        
        Important Notes:
        - Only use basic markdown formatting suitable for easy parsing.
        - Ensure all calculations are clearly presented.
        - If information is missing (e.g., unable to calculate duration from dates), state that clearly.
    """
