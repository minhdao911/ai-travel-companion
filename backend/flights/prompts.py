def flight_scrape_from_url_prompt(url, preferences):
    return f"""Follow these steps in order:
    Go to {url}
    1. Find and click the 'Search' button on the page

    2. If there is language selection popup, select 'English' and click on the 'OK' button to close the popup

    3. For the outbound flight (first leg of the journey):
        - Identify the best outbound flight based on user preferences: {preferences}
        - If no preferences are provided, select the cheapest and shortest outbound flight
        - Click on this outbound flight to select it
        - Store the outbound flight details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            * Stop Location and Time
            * Duration
            * Airlines and flight numbers
            * Origin and destination city names and airports

    4. For the return flight (second leg of the journey):
        - After selecting the outbound flight, you'll see return flight options
        - Identify the best return flight based on user preferences: {preferences}
        - If no preferences are provided, select the cheapest and shortest return flight
        - Store the return flight details including:
            * Departure time and date
            * Arrival time and date
            * Price
            * Number of stops
            * Stop Location and Time
            * Duration
            * Airlines
            * Origin and destination city names and airports

    5. Create a structured JSON response with both flights:
        {{
            "outbound_flight": {{
                "departure_date": "...",
                "departure_time": "...",
                "arrival_date": "...",
                "arrival_time": "...",
                "origin_city_name": "...",
                "destination_city_name": "...",
                "origin_airport_code": "...",
                "destination_airport_code": "...",
                "price": "",
                "num_stops": 0,
                "duration": "...",
                "airlines": "...",
                "stop_locations": "...",
            }},
            "return_flight": {{
                "departure_date": "...",
                "departure_time": "...",
                "arrival_date": "...",
                "arrival_time": "...",
                "origin_city_name": "...",
                "destination_city_name": "...",
                "origin_airport_code": "...",
                "destination_airport_code": "...",
                "price": "",
                "num_stops": 0,
                "duration": "...",
                "airlines": "...",
                "stop_locations": "...",
            }}
            "total_price": ""
        }}
        
    **Important:**
    - Make sure to capture BOTH outbound and return flight details
    - Each flight should have its own complete set of details
    - Store the duration in the format "Xh Ym" (e.g., "2h 15m")
    - Calculate the total price of the flight, which is the sum of outbound and return flight prices
    """
