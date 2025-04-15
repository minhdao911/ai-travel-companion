from ai.models import model
from travel.travel_schemas import travel_details_schema
from travel.prompts import travel_details_prompt, get_travel_summary_prompt

structured_model = model.with_structured_output(travel_details_schema)


def get_travel_details(input: str) -> dict:
    prompt = travel_details_prompt(input)
    try:
        return structured_model.invoke(prompt)
    except Exception as e:
        print(f"Error getting travel details: {str(e)}")
        raise ValueError(f"Error parsing user input: {e}")


def get_travel_summary(flights: str, hotels: str, **kwargs) -> str:
    prompt = get_travel_summary_prompt(flights, hotels, **kwargs)
    try:
        return model.invoke(prompt).content
    except Exception as e:
        print(f"Error getting travel summary: {str(e)}")
        raise SystemError(f"Error getting travel summary: {e}")
