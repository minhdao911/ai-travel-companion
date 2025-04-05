from ai.models import model

def get_travel_summary(flight_details: str, **kwargs) -> str:
    response = model.invoke(
        f"""Summarize the following flight and give me a nicely formatted output: 
        
        Given this information:
        Flight details: {flight_details}
                        
        Only used basic markdown formatting in your reply so it can be easily parsed by the frontend.
        """
    )
    return response.content
