from scrapers.brightdata_api import BrightDataAPI
from urllib.parse import urlencode, quote
import concurrent.futures


def get_hotel_details(
    location: str,
    checkin_date: str,
    checkout_date: str,
    num_guests: int,
    currency: str = "EUR",
    free_cancellation: bool = False,
    accommodation_types: list[str] = ["hotel"],
):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit both search functions to the executor
        hotels_future = executor.submit(
            search_hotels,
            location,
            checkin_date,
            checkout_date,
            num_guests,
            currency,
            free_cancellation,
            accommodation_types,
        )
        places_future = executor.submit(search_places, location, accommodation_types)

        # Wait for both futures to complete and get the results
        hotels = hotels_future.result()
        places = places_future.result()

    # Handle potential None results if API calls failed
    hotels = (
        list(filter(lambda x: x.get("link") is not None, hotels.get("organic", [])))
        if hotels
        else []
    )
    places = places.get("organic", []) if places else None

    hotel_details = []
    # Ensure places is searchable, assuming it's a list of dicts
    if isinstance(places, list) and len(places) > 0:
        for hotel in hotels:
            # Find the corresponding place using title
            place = next(
                (p for p in places if p.get("title") == hotel.get("title")), None
            )
            if place:
                enriched_hotel = hotel.copy()
                enriched_hotel["amenities"] = [
                    tag.get("value_title") for tag in place.get("tags", [])
                ]
                categories = place.get("category", [])
                enriched_hotel["category"] = (
                    categories[0].get("title") if categories else None
                )
                hotel_details.append(enriched_hotel)
    else:
        print("Skipping enrichment.")
        hotel_details = hotels if hotels else []

    return hotel_details


def search_hotels(
    location: str,
    checkin_date: str,
    checkout_date: str,
    num_guests: int,
    currency: str = "USD",
    free_cancellation: bool = False,
    accommodation_types: list[str] = ["hotel"],
):
    brightdata_api = BrightDataAPI()
    accommodation_types_str = " or ".join(accommodation_types)
    query = urlencode({"q": accommodation_types_str + " in " + location})
    url = f"https://www.google.com/travel/search?{query}"
    params = {
        "brd_dates": f"{checkin_date},{checkout_date}",
        "brd_occupancy": num_guests,
        "brd_currency": currency,
        "brd_free_cancellation": free_cancellation,
    }
    return brightdata_api.get_serp_results(url, params)


def search_places(
    location: str, accommodation_types: list[str] = ["hotel"], num_results: int = 30
):
    brightdata_api = BrightDataAPI()
    accommodation_types_str = " or ".join(accommodation_types)
    query = quote(accommodation_types_str + " in " + location)
    url = f"https://www.google.com/maps/search/{query}/?num={num_results}"
    return brightdata_api.get_serp_results(url)


def to_markdown(hotel_details: list[dict]) -> str:
    markdown = ""
    for hotel in hotel_details:
        title = hotel.get("title")
        link = hotel.get("link")
        markdown += f"**[{title}]({link})**\n" if link else f"**{title}**\n"

        category = hotel.get("category")
        markdown += f"* **Category:** {category}\n" if category else ""

        price = hotel.get("price")
        if price:
            markdown += f"* **Price:** {price}\n"

        amenities = hotel.get("amenities")
        markdown += f"* **Amenities:** {', '.join(amenities)}\n" if amenities else ""

        rating = hotel.get("rating")
        reviews_cnt = hotel.get("reviews_cnt")
        if rating is not None and reviews_cnt is not None:
            markdown += f"* **Rating:** {rating}/5 ({reviews_cnt} reviews)\n\n"
        else:
            markdown += "\n"
    return markdown
