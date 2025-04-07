def flight_scrape_from_url_prompt(url, preferences):
    return f"""Follow these steps in order:
    Go to {url}
    1. If there is language selection popup, select 'English' and click on the 'OK' button to close the popup

    2. For the outbound flight (first leg of the journey):
        - Identify 2 to 3 outbound flights based on user preferences: {preferences}
        - If no preferences are provided, select based on the price and duration
        - Store all selected outbound flights details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            * Stop Location and Time
            * Duration
            * Airlines
            * Origin and destination cities and airports
        - Click on one of the selected outbound flights to select it

    3. For the return flight (second leg of the journey):
        - After selecting the outbound flight, you'll see return flight options
        - Identify 2 to 3 return flights based on user preferences: {preferences}
        - If no preferences are provided, select based on the price and duration
        - Store all selected return flights details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            * Stop Location and Time
            * Duration
            * Airlines
            * Origin and destination cities and airports

    4. Return the details for both outbound and return flights in markdown format
        
    **Important:**
    - Make sure to capture BOTH outbound and return flight details
    - Each flight should have its own complete set of details
    - Store the duration in the format "Xh Ym" (e.g., "2h 15m")
    """

def hotel_scrape_from_url_prompt(url, preferences):
    return f"""Follow these steps in order:
    Go to {url}
    1. Identify 2 to 3 hotels based on user preferences: {preferences}
        - If no preferences are provided, prioritize hotels with high ratings, cheap price and good location

    2. Store the hotel details including:
        * Name
        * Price
        * Rating
        * Location
        * Amenities

    3. Return the details for all selected hotels in markdown format
    """