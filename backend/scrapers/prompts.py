def flight_scrape_from_url_prompt(url, preferences):
    return f"""Follow these steps in order:
    Go to {url}
    1. If there is language selection popup, select 'English' and click on the 'OK' button to close the popup

    2. For the outbound flight (first leg of the journey):
        - Identify 3 outbound flights based on user preferences: {preferences}
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
        - Identify 3 return flights based on user preferences: {preferences}
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

    4. Structure the response using basic markdown as shown below:
        **Outbound Flights:**
        [Outbound Flight 1 Details]
        [Outbound Flight 2 Details]
        [Outbound Flight 3 Details]

        **Return Flights:**
        [Return Flight 1 Details]
        [Return Flight 2 Details]
        [Return Flight 3 Details]

    **Important:**
    - Make sure to capture BOTH outbound and return flight details
    - Each flight should have its own complete set of details
    - Store the duration in the format "Xh Ym" (e.g., "2h 15m")
    - The final output must start directly with the markdown for the outbound flights and end immediately after the markdown for the return flights.
    """

def hotel_scrape_from_url_prompt(url, preferences):
    return f"""Follow these steps in order:
    Go to {url}
    1. Identify 3 hotels based on user preferences: {preferences}
        - If no preferences are provided, prioritize hotels with high ratings, cheap price and good location

    2. Store the hotel details including:
        * Name
        * Price
        * Rating
        * Location
        * Amenities

    3. Structure the response using basic markdown as shown below:
        **Hotels:**
        [Hotel 1 Details]
        [Hotel 2 Details]
        [Hotel 3 Details]
    """