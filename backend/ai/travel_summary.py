from ai.models import model

def get_travel_summary(flights: str, **kwargs) -> str:
    response = model.invoke(
        f"""Summarize the following flights and give me a nicely formatted output: 
        
        Given this information:
        Flights: {flights}

        Make the recommendation for the best combination (1 outbound and 1 return flight) based on the user preferences: {kwargs}.
        If no preferences are provided, make the recommendation based on the cheapest and shortest flights.
        Make sure to return only 1 combination (1 outbound and 1 return flight). and don't include other flight details.
        Calculate the total price of the selected combination which is the sum of the outbound and return flights.
        Only used basic markdown formatting in your reply so it can be easily parsed by the frontend.
        """
    )
    return response.content
