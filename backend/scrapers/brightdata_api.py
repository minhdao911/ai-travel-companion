from dotenv import load_dotenv
import os
from typing import Dict, Any, Optional
import requests
import time

load_dotenv()


class BrightDataAPI:
    """
    BrightData API for scraping Google SERP results
    """

    base_url = "https://api.brightdata.com/serp"

    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.customer_id = os.getenv("BRIGHT_DATA_CUSTOMER_ID")
        self.api_zone = os.getenv("BRIGHT_DATA_API_ZONE")
        self.session = self._create_session()

    def _create_session(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        with requests.Session() as session:
            session.headers = headers
            session.params = {"customer": self.customer_id, "zone": self.api_zone}
            return session

    def _poll_results(
        self, response_id: str, max_retries: int = 5, delay: int = 5
    ) -> Optional[Dict]:
        url = f"{self.base_url}/get_result"
        self.session.params["response_id"] = response_id

        for _ in range(max_retries):
            response = self.session.get(url)
            response.raise_for_status()
            try:
                data = response.json()
                print(f"{response_id}: Completed")
                return data
            except ValueError as e:
                print(f"{response_id}: {response.text[:200]}")

            time.sleep(delay)

        print(f"{response_id}: Max retries reached")
        return None

    def get_serp_results(
        self, url: str, params: Dict[str, Any] = None
    ) -> Optional[Dict]:
        payload = {"url": url + "&brd_json=1"}

        if params:
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            if "?" in payload["url"]:
                payload["url"] += f"&{query_params}"
            else:
                payload["url"] += f"?{query_params}"

        try:
            response = self.session.post(
                f"{self.base_url}/req",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            response_id = data.get("response_id")
            if response_id:
                print(f"Request: {payload}", f"Response ID: {response_id}")
                return self._poll_results(response_id)
            else:
                raise Exception("No response ID returned")
        except requests.exceptions.RequestException as e:
            print(f"HTTP error while fetching SERP results: {e}")
            return None
        except Exception as e:
            print(f"Error fetching SERP results: {e}")
            return None
