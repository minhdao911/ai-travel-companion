from playwright.async_api import async_playwright
from browser_use import Browser, Agent, BrowserConfig
from ai.models import model
from scrapers.prompts import hotel_scrape_from_url_prompt

class HotelScraper:
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
    
    async def select_dates(self, start_date, end_date):
        try:
            await self.page.click('input[aria-label*="Check-in"]')
            await self.page.wait_for_timeout(1000)

            # Select departure date
            start_date_element = await self.page.wait_for_selector(f"div[role='gridcell'][data-iso='{start_date}']", timeout=5000)
            await start_date_element.click()
            await self.page.wait_for_timeout(1000)

            # Select return date
            end_date_element = await self.page.wait_for_selector(f"div[role='gridcell'][data-iso='{end_date}']", timeout=5000)
            await end_date_element.click()
            await self.page.wait_for_timeout(1000)

            # Close the date picker
            await self.page.click('header')

            print(f"Selected dates: {start_date} - {end_date}")
            return True
        except Exception as e:
            print(f"Error selecting dates: {str(e)}")
            return False
    
    async def select_num_guests(self, num_guests):
        try:
            await self.page.click('button[data-adults]')

            # Wait for the modal to appear
            count = 1
            add_button = await self.page.wait_for_selector("button[aria-label*='Add adult']", timeout=5000)
            while count < num_guests:
                await add_button.click()
                count += 1

            # Close the modal
            await self.page.click('button[data-adults]')

            print(f"Selected number of guests: {num_guests} adults")
            return True
        except Exception as e:
            print(f"Error selecting number of guests: {str(e)}")
            return False
        
    async def fill_hotel_search(self, destination, start_date, end_date, num_guests):
        try:
            print("Navigating to Google Hotels")
            await self.page.goto(f"https://www.google.com/travel/search?q=hotels+in+{destination}")

            # Check if accept cookies button is visible
            accept_cookies_button = await self.page.wait_for_selector('button[aria-label="Accept all"]', timeout=5000)
            if accept_cookies_button:
                await accept_cookies_button.click()

            print("Selecting dates")
            if not await self.select_dates(start_date, end_date):
                raise Exception("Error selecting dates")
            
            print("Filling number of guests")
            if num_guests > 1:
                if not await self.select_num_guests(num_guests):
                    raise Exception("Error selecting number of guests")

            return self.page.url

        except Exception as e:
            print(f"Error filling hotel search: {str(e)}")
            return None

async def scrape_hotels(url, preferences = None):
    try:
        config = BrowserConfig(headless=True)
        browser = Browser(config)
        agent = Agent(
            task=hotel_scrape_from_url_prompt(url, preferences),
            browser=browser,
            llm=model
        )

        history = await agent.run()
        await browser.close()
        result = history.final_result()
        return result
    except Exception as e:
        print(f"Error scraping hotels: {str(e)}")
        return None        

async def get_hotel_search_url(destination, start_date, end_date, num_guests):
    try:
        scraper = HotelScraper()
        await scraper.start()
        url = await scraper.fill_hotel_search(destination, start_date, end_date, num_guests)
        return url
    except Exception as e:
        print(f"Error getting hotel URL: {str(e)}")
    finally:
        print("Closing browser")
        await scraper.close()