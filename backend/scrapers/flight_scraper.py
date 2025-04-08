from playwright.async_api import async_playwright
from browser_use import Browser, Agent, BrowserConfig
from ai.models import model
from scrapers.prompts import flight_scrape_from_url_prompt

class FlightScraper:
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def close(self):
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
        except Exception as e:
            print(f"Error during playwright cleanup: {str(e)}")

    async def fill_and_select_city(self, input_element, city_name):
        try:
            await input_element.type(city_name, delay=50)
            await self.page.wait_for_timeout(1000)

            # Wait for the dropdown to appear
            dropdown_item = await self.page.wait_for_selector(f"li[role='option'][aria-label^='{city_name}']", timeout=5000)
            if dropdown_item:
                # Click on the suggestion that starts with the city name
                await dropdown_item.click()
                await self.page.wait_for_load_state("networkidle")

                print(f"Selected city: {city_name}")
                return True
            
            raise Exception(f"Could not select city: {city_name}")
            
        except Exception as e:
            print(f"Error filling and selecting city: {str(e)}")
            return False
    
    async def select_dates(self, start_date, end_date):
        try:
            await self.page.click('input[aria-label*="Departure"]')
            await self.page.wait_for_timeout(1000)

            # Select departure date
            start_date_element = await self.page.wait_for_selector(f"div[role='gridcell'][data-iso='{start_date}']", timeout=5000)
            await start_date_element.click()
            await self.page.wait_for_timeout(1000)

            # Select return date
            end_date_element = await self.page.wait_for_selector(f"div[role='gridcell'][data-iso='{end_date}']", timeout=5000)
            await end_date_element.click()
            await self.page.wait_for_timeout(1000)

            # Click on the done button
            await self.page.locator('button[aria-label*="Done."]').click()

            print(f"Selected dates: {start_date} - {end_date}")
            return True
        except Exception as e:
            print(f"Error selecting dates: {str(e)}")
            return False
    
    async def select_num_guests(self, num_guests):
        try:
            await self.page.click('button[aria-label*="passenger"]')

            # Wait for the modal to appear
            count = 1
            add_button = await self.page.wait_for_selector("button[aria-label*='Add adult']", timeout=5000)
            while count < num_guests:
                await add_button.click()
                count += 1

            # Close the modal
            await self.page.click('button[aria-label*="passenger"]')

            print(f"Selected number of guests: {num_guests} adults")
            return True
        except Exception as e:
            print(f"Error selecting number of guests: {str(e)}")
            return False
        
    async def fill_flight_search(self, origin, destination, start_date, end_date, num_guests):
        try:
            print("Navigating to Google Flights")
            await self.page.goto("https://www.google.com/travel/flights")

            # Check if accept cookies button is visible
            accept_cookies_button = await self.page.wait_for_selector('button[aria-label="Accept all"]', timeout=5000)
            if accept_cookies_button:
                await accept_cookies_button.click()

            print("Filling origin")
            origin_input_element = await self.page.wait_for_selector('input[aria-label*="Where from?"]', timeout=5000)
            await origin_input_element.click()
            await self.page.wait_for_timeout(500)

            # Clear the input field before typing
            await origin_input_element.press("Control+a")
            await origin_input_element.press("Delete")
            await self.page.wait_for_timeout(500)

            if not await self.fill_and_select_city(origin_input_element, origin):
                raise Exception("Error filling and selecting origin")

            print("Filling destination")
            destination_input_element = await self.page.wait_for_selector('input[aria-label*="Where to?"]', timeout=5000)
            if not await self.fill_and_select_city(destination_input_element, destination):
                raise Exception("Error filling and selecting destination")
            
            print("Filling number of guests")
            if num_guests > 1:
                if not await self.select_num_guests(num_guests):
                    raise Exception("Error selecting number of guests")

            print("Selecting dates")
            if not await self.select_dates(start_date, end_date):
                raise Exception("Error selecting dates")
            
            # Click on the search button
            await self.page.locator('button[aria-label="Search"]').click()
            await self.page.wait_for_timeout(2000)

            return self.page.url

        except Exception as e:
            print(f"Error filling flight search: {str(e)}")
            return None

async def scrape_flights(url, preferences = None):
    try:
        config = BrowserConfig(headless=True)
        browser = Browser(config)
        agent = Agent(
            task=flight_scrape_from_url_prompt(url, preferences),
            browser=browser,
            llm=model
        )

        history = await agent.run()
        await browser.close()
        result = history.final_result()
        return result
    except Exception as e:
        print(f"Error scraping flights: {str(e)}")
        return None        

async def get_flight_search_url(origin, destination, start_date, end_date, num_guests):
    try:
        scraper = FlightScraper()
        await scraper.start()
        url = await scraper.fill_flight_search(origin, destination, start_date, end_date, num_guests)
        return url
    except Exception as e:
        print(f"Error getting flight URL: {str(e)}")
    finally:
        print("Closing browser")
        await scraper.close()