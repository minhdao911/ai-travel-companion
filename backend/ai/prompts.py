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

def travel_details_prompt(input: str) -> str:
    return f"""
        Read the following information from the user and extract the data into the structured output fields.
        
        {input}

        When providing dates give the format like this: 2025-05-02
        When providing times give the format like this: 03:00 PM
        when providing stop locations give the city and airport code like this: Paris (CDG), if you don't know the city, just give the airport code
        When providing airlines and flight numbers give the format like this: Air France (AF 1234)
        If you don't know the origin or destination city, don't fill in the airport code, leave the city name empty.
    """