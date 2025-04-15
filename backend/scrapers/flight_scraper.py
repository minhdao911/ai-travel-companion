from fast_flights import FlightData as FastFlightsFlightData, Passengers, create_filter
from urllib.parse import urlencode
import requests
from selectolax.parser import HTMLParser
from pydantic import BaseModel
from typing import List
import re
from datetime import datetime
import hashlib
from utils.datetime import format_date


class FlightPrice(BaseModel):
    amount: int
    currency: str


class FlightStopLocation(BaseModel):
    city: str
    airport: str
    duration: str


class FlightPreferences(BaseModel):
    seat_class: str
    direct: bool


class FlightData(BaseModel):
    id: str | None = None
    departure_date: str | None = None
    departure_time: str | None = None
    arrival_date: str | None = None
    arrival_time: str | None = None
    origin: str | None = None
    destination: str | None = None
    price: FlightPrice | None = None
    num_stops: int | None = None
    duration: str | None = None
    airlines: list[str] = []
    stop_locations: List[FlightStopLocation] = []
    preferences: FlightPreferences | None = None


def _parse_duration_to_minutes(duration_str: str | None) -> int | None:
    """Converts duration string (e.g., '10 hr 30 min', '5 hr', '45 min') to total minutes."""
    if not duration_str:
        return None

    hours = 0
    minutes = 0

    hour_match = re.search(r"(\d+)\s*hr", duration_str)
    if hour_match:
        hours = int(hour_match.group(1))

    min_match = re.search(r"(\d+)\s*min", duration_str)
    if min_match:
        minutes = int(min_match.group(1))

    if hours > 0 or minutes > 0:
        total_minutes = hours * 60 + minutes
        return total_minutes
    else:
        return None


def _parse_date(date_str, year):
    """Parses date strings like 'Thursday, May 1' into 'YYYY-MM-DD'."""
    try:
        if ", " in date_str:
            date_part = date_str.split(", ")[1]
        else:
            date_part = date_str
        full_date_str = f"{date_part}, {year}"
        dt_obj = datetime.strptime(full_date_str, "%B %d, %Y")
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "Invalid Date Format"


def _currency_to_currency_code(currency: str) -> str:
    # Note: This assumes the scraped currency string ends with 's' (e.g., "euros", "dollars")
    currency_map = {
        "euro": "EUR",
        "dollar": "USD",
        "pound": "GBP",
    }
    return currency_map.get(currency.lower(), "UNK")  # Return UNK for unknown


def _cheapest_flight_key(flight: FlightData):
    price = (
        flight.price.amount
        if flight.price and flight.price.amount is not None
        else float("inf")
    )
    return price


def _shortest_flight_key(flight: FlightData):
    duration_minutes = _parse_duration_to_minutes(flight.duration)
    duration = duration_minutes if duration_minutes is not None else float("inf")
    return duration


def to_markdown(flights: List[FlightData]):
    content = ""
    for index, flight in enumerate(flights):
        content += f"Flight {index + 1}:\n"
        content += f"* **Departure:** {format_date(flight.departure_date)} {flight.departure_time} from {flight.origin}\n"
        content += f"* **Arrival:** {format_date(flight.arrival_date)} {flight.arrival_time} at {flight.destination}\n"
        content += f"* **Duration:** {flight.duration}\n"
        content += f"* **Stops:** {flight.num_stops}\n"
        content += f"* **Airlines:** {', '.join(flight.airlines)}\n"
        content += f"* **Price:** {flight.price.amount} {flight.price.currency}\n"
        content += f"* **Layovers:**\n"
        for stop in flight.stop_locations:
            content += f"  * {stop.city} ({stop.airport}) for {stop.duration}\n"
        content += "\n"
    return content


def to_json(flights: List[FlightData]):
    return [flight.model_dump() for flight in flights]


class FlightScraper:
    """
    Scrapes Google Flights for flight information based on provided criteria.
    """

    def __init__(
        self,
        origin_airport_code,
        destination_airport_code,
        num_guests=1,
        preferences={"seat_class": "economy", "direct": False},
    ):
        self.origin_airport_code = origin_airport_code
        self.destination_airport_code = destination_airport_code
        self.date = None
        self.num_guests = num_guests
        self.preferences = FlightPreferences(**preferences)

        self.html_content = None
        self.raw_flight_strings = []
        self.parsed_flights: List[FlightData] = []
        self.best_flights: List[FlightData] = []

    def _get_flight_url(self) -> str:
        """Constructs the Google Flights URL."""
        filter_obj = create_filter(
            flight_data=[
                FastFlightsFlightData(
                    date=self.date,
                    from_airport=self.origin_airport_code,
                    to_airport=self.destination_airport_code,
                )
            ],
            trip="one-way",
            seat=self.preferences.seat_class,
            max_stops=0 if self.preferences.direct else None,
            passengers=Passengers(adults=self.num_guests),
        )

        params = {
            "tfs": filter_obj.as_b64().decode("utf-8"),
            "hl": "en",
            "tfu": "EgQIABABIgA",
        }
        return f"https://www.google.com/travel/flights?{urlencode(params)}"

    def _fetch_flight_html(self) -> bool:
        """Fetches the HTML content from the Google Flights URL."""
        url = self._get_flight_url()
        print(f"Fetching flights from: {url}")
        try:
            response = requests.get(url, timeout=30)  # Added timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            self.html_content = response.text
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching flight data: {e}")
            self.html_content = None
            return False

    def _extract_flight_strings(self):
        """Extracts raw flight description strings from the HTML."""
        if not self.html_content:
            print("HTML content not available for parsing.")
            self.raw_flight_strings = []
            return

        tree = HTMLParser(self.html_content)
        nodes = tree.css("div[aria-label*='Select flight']")
        self.raw_flight_strings = [
            node.attributes.get("aria-label", "")
            for node in nodes
            if node.attributes.get("aria-label")
        ]

    def _parse_flight_data(self):
        """Parses structured flight data from the raw description strings."""
        if not self.raw_flight_strings or len(self.raw_flight_strings) == 0:
            print("No raw flight strings to parse.")
            self.parsed_flights = []
            return

        print(f"Parsing {len(self.raw_flight_strings)} potential flight strings...")
        parsed_flights_temp = []
        year = datetime.strptime(self.date, "%Y-%m-%d").year
        seen_ids = set()  # To track duplicates based on generated ID

        for line in self.raw_flight_strings:
            flight_info = FlightData()
            line = line.replace("\u202f", " ")  # Clean unicode spaces

            # Price
            price_match = re.search(
                r"From (\d{1,3}(?:,\d{3})*|\d+) (\w+)", line
            )  # Improved price regex
            if price_match:
                currency = price_match.group(2).lower()
                # Handle potential 's' at the end (euros, dollars)
                if currency.endswith("s"):
                    currency = currency[:-1]
                flight_info.price = FlightPrice(
                    amount=int(price_match.group(1).replace(",", "")),
                    currency=_currency_to_currency_code(currency),
                )
            elif "Total price is unavailable" in line:
                flight_info.price = None  # Explicitly set to None

            # Stops
            stops_match = re.search(r"(\d+) stop(?:s)? flight", line)
            if stops_match:
                flight_info.num_stops = int(stops_match.group(1))
            elif "Nonstop flight" in line:
                flight_info.num_stops = 0
            else:
                flight_info.num_stops = None  # Explicitly set None if not found

            # Duration
            duration_match = re.search(r"Total duration (.*?)\.", line)
            if duration_match:
                flight_info.duration = duration_match.group(1).strip()

            # Departure Info
            dep_match = re.search(
                r"Leaves (.*?) Airport at (\d{1,2}:\d{2}\s?[AP]M) on (.*?) and", line
            )  # Added optional space before AM/PM
            if dep_match:
                dep_airport_name = dep_match.group(1).strip()
                flight_info.departure_time = (
                    dep_match.group(2).strip().replace(" ", "")
                )  # Remove space
                dep_date_str = dep_match.group(3).strip()
                flight_info.departure_date = _parse_date(dep_date_str, year)
                flight_info.origin = f"{dep_airport_name} ({self.origin_airport_code})"

            # Arrival Info
            arr_match = re.search(
                r"arrives at (.*?) Airport(?: at (\d{1,2}:\d{2}\s?[AP]M))? on (.*?)\.",
                line,
            )  # Made time optional
            if arr_match:
                arr_airport_name = arr_match.group(1).strip()
                flight_info.arrival_time = (
                    arr_match.group(2).strip().replace(" ", "")
                    if arr_match.group(2)
                    else None
                )
                arr_date_str = arr_match.group(3).strip()
                flight_info.arrival_date = _parse_date(arr_date_str, year)
                flight_info.destination = (
                    f"{arr_airport_name} ({self.destination_airport_code})"
                )

            # Airlines - More robust extraction
            # Try common patterns first
            airline_match = re.search(
                r"flight with (.*?)(?: operated by .*?)?(?: arriving| \.|\.|$)",
                line,
                re.IGNORECASE,
            )
            if not airline_match:
                # Fallback if "flight with" isn't present (e.g., just airline name)
                airline_match = re.search(
                    r"^(.*?) flight(?: from|\.|$)", line, re.IGNORECASE
                )  # Match airline at the start

            if airline_match:
                airlines_str = airline_match.group(1).strip().rstrip(".")
                # Remove phrases like "is a Nonstop" or similar if caught
                airlines_str = re.sub(
                    r"\s+is\s+a\s+\w+$", "", airlines_str, flags=re.IGNORECASE
                )
                flight_info.airlines = [
                    a.strip()
                    for a in re.split(r"\s+and\s+|, ", airlines_str)
                    if a.strip()
                ]
            else:
                flight_info.airlines = []  # Set to empty list if not found

            # Layovers / Stop Locations
            layover_matches = re.findall(
                r"Layover \(\d+ of \d+\) is a (.*?) layover at (.*?) in (.*?)\.", line
            )
            stops = []
            for layover in layover_matches:
                layover_duration = layover[0].strip()
                layover_airport = layover[1].strip()
                layover_city = layover[2].strip()
                stops.append(
                    FlightStopLocation(
                        city=layover_city,
                        airport=layover_airport,
                        duration=layover_duration,
                    )
                )
            flight_info.stop_locations = stops

            # Generate a unique ID for the flight based on its core details
            # Use a tuple of key fields for hashing to avoid issues with model string representation
            key_fields = (
                flight_info.departure_date,
                flight_info.departure_time,
                flight_info.arrival_date,
                flight_info.arrival_time,
                flight_info.origin,
                flight_info.destination,
                flight_info.num_stops,
                flight_info.duration,
                tuple(sorted(flight_info.airlines)),  # Sort airlines for consistency
                flight_info.price.amount if flight_info.price else None,
            )
            flight_info.id = hashlib.sha256(str(key_fields).encode()).hexdigest()

            # Append only if essential data is present and it's not a duplicate
            if (
                flight_info.departure_time
                and flight_info.arrival_date
                and flight_info.id not in seen_ids
            ):
                parsed_flights_temp.append(flight_info)
                seen_ids.add(flight_info.id)

        self.parsed_flights = parsed_flights_temp
        print(f"Successfully parsed {len(self.parsed_flights)} unique flights.")

    def _filter_best_flights(self) -> List[FlightData]:
        """
        Selects the top 3 cheapest flights and the 2 flights with the best
        combined rank (shortest position + cheapest position) from the remainder.
        Returns copies to avoid modifying the main list.
        """
        if not self.parsed_flights:
            return []

        num_flights = len(self.parsed_flights)
        if num_flights <= 5:
            # If 5 or fewer flights, return them sorted by price
            return sorted(self.parsed_flights, key=_cheapest_flight_key)[:5]

        # Sort flights by price and duration
        # Make copies to avoid modifying the original list during sorting
        flights_copy = self.parsed_flights[:]
        cheapest_flights_sorted = sorted(flights_copy, key=_cheapest_flight_key)
        shortest_flights_sorted = sorted(flights_copy, key=_shortest_flight_key)

        # Create position maps for quick lookup using the flight IDs
        cheap_pos_map = {
            flight.id: i for i, flight in enumerate(cheapest_flights_sorted)
        }
        short_pos_map = {
            flight.id: i for i, flight in enumerate(shortest_flights_sorted)
        }

        # Select the top 3 cheapest flights (by ID)
        top_cheapest_ids = {flight.id for flight in cheapest_flights_sorted[:3]}

        # Calculate combined rank for remaining flights
        ranked_candidates = []
        for (
            flight
        ) in self.parsed_flights:  # Iterate original list to maintain original objects
            if flight.id not in top_cheapest_ids:
                # Ensure the flight ID exists in both maps (it should, barring errors)
                if flight.id in cheap_pos_map and flight.id in short_pos_map:
                    combined_rank = cheap_pos_map[flight.id] + short_pos_map[flight.id]
                    ranked_candidates.append((combined_rank, flight))
                else:
                    print(
                        f"Warning: Flight ID {flight.id} missing from position maps during ranking."
                    )

        # Sort candidates by the combined rank (lower is better)
        ranked_candidates.sort(key=lambda x: x[0])

        # Get the actual FlightData objects for the top 3 cheapest
        top_cheapest = [
            flight for flight in self.parsed_flights if flight.id in top_cheapest_ids
        ]
        # Ensure top_cheapest maintains the original price sort order
        top_cheapest.sort(key=_cheapest_flight_key)

        # Select the top 2 candidates based on combined rank
        additional_flights = [flight for rank, flight in ranked_candidates[:2]]

        # Combine the lists
        best_flights = top_cheapest + additional_flights

        # Ensure we don't exceed 5 flights due to edge cases
        return best_flights[:5]

    def get_flight_details(self, date: str) -> List[FlightData]:
        """
        Fetches, parses, and filters flight details, returning the best options.
        """
        self.date = date
        if not self._fetch_flight_html():
            return []  # Return empty list if fetching failed

        self._extract_flight_strings()
        self._parse_flight_data()

        if not self.parsed_flights:
            print("No flights found or parsed.")
            return []

        best_flights_data = self._filter_best_flights()
        self.best_flights = best_flights_data
        print(f"Selected {len(best_flights_data)} best flights.")

        return best_flights_data
