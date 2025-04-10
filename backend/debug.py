#!/usr/bin/env python3
import argparse
import json
import os
import sys
import asyncio
import datetime

# Add the current directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the backend modules
from travel.travel_details import generate_conversation_response, get_travel_summary
from scrapers.flight_scraper import get_flight_search_url, scrape_flights
from scrapers.hotel_scraper import get_hotel_search_url, scrape_hotels
from tasks import TaskManager
from main import MessageItem
from scrapers.flight_scraper_v2 import FlightScraperV2, to_json, to_markdown

# Create a task manager instance
task_manager = TaskManager()

class Debug:
    def __init__(self):
        self.parser = self._create_parser()
        self.commands = {
            'health': {
                'help': 'Check health of the API',
                'args': []
            },
            'travel-details': {
                'help': 'Generate travel conversation response',
                'args': [
                    {'name': 'user_input', 'type': str, 'required': True, 'help': 'User input message'},
                ]
            },
            'search-flights': {
                'help': 'Search for flights',
                'args': [
                    {'name': 'origin', 'type': str, 'required': True, 'help': 'Origin city name'},
                    {'name': 'destination', 'type': str, 'required': True, 'help': 'Destination city name'},
                    {'name': 'start_date', 'type': str, 'required': True, 'help': 'Start date (YYYY-MM-DD)'},
                    {'name': 'end_date', 'type': str, 'required': True, 'help': 'End date (YYYY-MM-DD)'},
                    {'name': 'num_guests', 'type': int, 'required': True, 'help': 'Number of guests'},
                    {'name': 'budget', 'type': int, 'required': False, 'help': 'Budget (optional)'},
                    {'name': 'preferences', 'type': str, 'required': False, 'help': 'Travel preferences (optional)'}
                ]
            },
            'search-hotels': {
                'help': 'Search for hotels',
                'args': [
                    {'name': 'destination', 'type': str, 'required': True, 'help': 'Destination city name'},
                    {'name': 'start_date', 'type': str, 'required': True, 'help': 'Start date (YYYY-MM-DD)'},
                    {'name': 'end_date', 'type': str, 'required': True, 'help': 'End date (YYYY-MM-DD)'},
                    {'name': 'num_guests', 'type': int, 'required': True, 'help': 'Number of guests'},
                    {'name': 'budget', 'type': int, 'required': False, 'help': 'Budget (optional)'},
                    {'name': 'preferences', 'type': str, 'required': False, 'help': 'Travel preferences (optional)'}
                ]
            },
            'travel-summary': {
                'help': 'Generate travel summary',
                'args': [
                    {'name': 'start_date', 'type': str, 'required': True, 'help': 'Start date (YYYY-MM-DD)'},
                    {'name': 'end_date', 'type': str, 'required': True, 'help': 'End date (YYYY-MM-DD)'},
                    {'name': 'num_guests', 'type': int, 'required': True, 'help': 'Number of guests'},
                    {'name': 'flight_results', 'type': str, 'required': True, 'help': 'Flight results string or file path'},
                    {'name': 'hotel_results', 'type': str, 'required': True, 'help': 'Hotel results string or file path'},
                    {'name': 'budget', 'type': int, 'required': False, 'help': 'Budget (optional)'},
                    {'name': 'preferences', 'type': str, 'required': False, 'help': 'Travel preferences (optional)'}
                ]
            },
            'flights-hotels-summary': {
                'help': 'Search for flights and hotels and generate summary',
                'args': [
                    {'name': 'origin', 'type': str, 'required': True, 'help': 'Origin city name'},
                    {'name': 'destination', 'type': str, 'required': True, 'help': 'Destination city name'},
                    {'name': 'start_date', 'type': str, 'required': True, 'help': 'Start date (YYYY-MM-DD)'},
                    {'name': 'end_date', 'type': str, 'required': True, 'help': 'End date (YYYY-MM-DD)'},
                    {'name': 'num_guests', 'type': int, 'required': True, 'help': 'Number of guests'},
                    {'name': 'budget', 'type': int, 'required': False, 'help': 'Budget (optional)'},
                    {'name': 'preferences', 'type': str, 'required': False, 'help': 'Travel preferences (optional)'}
                ]
            }
        }
        
    def _create_parser(self):
        parser = argparse.ArgumentParser(description='Test AI Travel Companion Backend Functions')
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # Debug mode command
        debug_parser = subparsers.add_parser('debug', help='Run in interactive debug mode')
        
        # Health check command
        health_parser = subparsers.add_parser('health', help='Check health of the API')
        
        # Travel details command
        travel_details_parser = subparsers.add_parser('travel-details', help='Generate travel conversation response')
        travel_details_parser.add_argument('--user-input', type=str, required=True, help='User input message')
        
        # Search flights command
        flights_parser = subparsers.add_parser('search-flights', help='Search for flights')
        flights_parser.add_argument('--origin', type=str, required=True, help='Origin city name')
        flights_parser.add_argument('--destination', type=str, required=True, help='Destination city name')
        flights_parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
        flights_parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
        flights_parser.add_argument('--num-guests', type=int, required=True, help='Number of guests')
        flights_parser.add_argument('--budget', type=int, help='Budget (optional)')
        flights_parser.add_argument('--preferences', type=str, help='Travel preferences (optional)')
        
        # Search hotels command
        hotels_parser = subparsers.add_parser('search-hotels', help='Search for hotels')
        hotels_parser.add_argument('--destination', type=str, required=True, help='Destination city name')
        hotels_parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
        hotels_parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
        hotels_parser.add_argument('--num-guests', type=int, required=True, help='Number of guests')
        hotels_parser.add_argument('--budget', type=int, help='Budget (optional)')
        hotels_parser.add_argument('--preferences', type=str, help='Travel preferences (optional)')
        
        # Travel summary command
        summary_parser = subparsers.add_parser('travel-summary', help='Generate travel summary')
        summary_parser.add_argument('--destination', type=str, required=True, help='Destination city name')
        summary_parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
        summary_parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
        summary_parser.add_argument('--num-guests', type=int, required=True, help='Number of guests')
        summary_parser.add_argument('--flight-results', type=str, required=True, help='Flight results string or file path')
        summary_parser.add_argument('--hotel-results', type=str, required=True, help='Hotel results string or file path')
        summary_parser.add_argument('--budget', type=int, help='Budget (optional)')
        summary_parser.add_argument('--preferences', type=str, help='Travel preferences (optional)')

        # Flights and hotels summary command
        flights_hotels_summary_parser = subparsers.add_parser('flights-hotels-summary', help='Search for flights and hotels and generate summary')
        flights_hotels_summary_parser.add_argument('--origin', type=str, required=True, help='Origin city name')
        flights_hotels_summary_parser.add_argument('--destination', type=str, required=True, help='Destination city name')
        flights_hotels_summary_parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
        flights_hotels_summary_parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
        flights_hotels_summary_parser.add_argument('--num-guests', type=int, required=True, help='Number of guests')
        flights_hotels_summary_parser.add_argument('--budget', type=int, help='Budget (optional)')
        flights_hotels_summary_parser.add_argument('--preferences', type=str, help='Travel preferences (optional)')
        
        # List available commands
        list_parser = subparsers.add_parser('list', help='List available commands')
        
        return parser
    
    def run(self, args=None):
        args = self.parser.parse_args(args)
        
        if args.command == 'debug':
            self._run_debug_mode()
            return
        
        if not args.command or args.command == 'list':
            self.parser.print_help()
            return
        
        if args.command == 'health':
            self._health_check()
        elif args.command == 'travel-details':
            asyncio.run(self._travel_details(args))
        elif args.command == 'search-flights':
            asyncio.run(self._search_flights(args))
        elif args.command == 'search-hotels':
            asyncio.run(self._search_hotels(args))
        elif args.command == 'travel-summary':
            asyncio.run(self._travel_summary(args))
    
    def _run_debug_mode(self):
        """Run the application in interactive debug mode"""
        while True:
            print("\n=== AI TRAVEL COMPANION DEBUG MODE ===")
            print("Available commands:")
            
            # Display available commands
            for i, (cmd, details) in enumerate(self.commands.items(), 1):
                print(f"{i}. {cmd} - {details['help']}")
            print("0. Exit")
            
            # Get command choice
            choice = input("\nEnter command number: ")
            if choice == '0':
                print("Exiting debug mode...")
                break
                
            try:
                choice_idx = int(choice) - 1
                if choice_idx < 0 or choice_idx >= len(self.commands):
                    print("Invalid choice. Please try again.")
                    continue
                    
                # Get selected command
                cmd_name = list(self.commands.keys())[choice_idx]
                
                # Execute the command with retry logic
                self._execute_command_with_retry(cmd_name)
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _execute_command_with_retry(self, cmd_name):
        """Execute a command with retry functionality"""
        cmd_details = self.commands[cmd_name]
        retry = True
        
        # Store previous arguments for potential reuse
        previous_args = None
        
        while retry:
            print(f"\nRunning command: {cmd_name}")
            
            # Get arguments for the command
            if previous_args and input("Use same arguments as before? (y/n): ").lower() == 'y':
                args = previous_args
            else:
                # Prompt for new arguments
                args = {}
                for arg in cmd_details['args']:
                    while True:
                        prompt = f"{arg['name']} ({arg['help']}): "
                        if not arg['required']:
                            prompt += "(optional, press Enter to skip) "
                            
                        value = input(prompt)
                        
                        # Skip optional arguments if no value provided
                        if not value and not arg['required']:
                            break
                            
                        # Validate required arguments
                        if not value and arg['required']:
                            print(f"Error: {arg['name']} is required. Please provide a value.")
                            continue
                            
                        # Convert value to appropriate type
                        try:
                            if arg['type'] == int:
                                value = int(value)
                            args[arg['name']] = value
                            break
                        except ValueError:
                            print(f"Error: {arg['name']} must be a {arg['type'].__name__}. Please try again.")
                
                # Save arguments for potential reuse
                previous_args = args.copy()
            
            # Create namespace object from arguments
            namespace = argparse.Namespace(**args)
            
            # Execute command
            try:
                if cmd_name == 'health':
                    self._health_check()
                elif cmd_name == 'travel-details':
                    asyncio.run(self._travel_details(namespace))
                elif cmd_name == 'search-flights':
                    asyncio.run(self._search_flights(namespace))
                elif cmd_name == 'search-hotels':
                    asyncio.run(self._search_hotels(namespace))
                elif cmd_name == 'travel-summary':
                    asyncio.run(self._travel_summary(namespace))
            except Exception as e:
                print(f"\nCommand execution failed: {str(e)}")
            
            # Ask if user wants to retry the command
            retry_choice = input("\nDo you want to: [r]etry, [m]ain menu, or [q]uit? (r/m/q): ").lower()
            if retry_choice == 'r':
                retry = True
            elif retry_choice == 'q':
                print("Exiting debug mode...")
                sys.exit(0)
            else:
                retry = False
    
    def _health_check(self):
        print(json.dumps({"status": "ok", "message": "API is running"}, indent=2))
    
    async def _travel_details(self, args):
        try:
            conversation_history = []

            # --- Start Interactive Conversation Loop ---
            current_user_input = args.user_input
            print(f"\nStarting conversation...")
            print(f"You: {current_user_input}") # Echo user input

            while True:
                # Add user message to history
                conversation_history.append(MessageItem(role="user", content=current_user_input))

                # Generate response
                print("AI is thinking...")
                # Assuming generate_conversation_response takes List[MessageItem] and returns a dict/object
                # with 'content' and 'complete' attributes/keys.
                # Ensure generate_conversation_response is awaitable if called with await
                response_data = generate_conversation_response(conversation_history)

                # Extract message and completion status
                ai_message = response_data.message
                is_complete = response_data.complete
            
                # Print AI response
                print(f"AI: {ai_message}")
                
                # Add AI response to history
                conversation_history.append(MessageItem(role="assistant", content=ai_message))

                # Check if conversation is complete
                if is_complete:
                    print("\nConversation complete.")
                    print(f"Travel preferences: {response_data.travel_preferences}")
                    break

                # Prompt for next user input
                next_input = input("You: ").strip()
                if not next_input:
                    print("\nEmpty input received. Ending conversation.")
                    break
                current_user_input = next_input
            # --- End Interactive Conversation Loop ---

            print("\nExiting travel details conversation.")

        except Exception as e:
            print(f"Error during conversation processing: {str(e)}")
    
    async def _search_flights(self, args):
        try:
            print(f"Searching for flights from {args.origin} to {args.destination}...")
            
            # --- v1 ---
            # Get flight search URL
            # url = await get_flight_search_url(
            #     args.origin, 
            #     args.destination, 
            #     args.start_date, 
            #     args.end_date, 
            #     args.num_guests
            # )
            
            # if not url:
            #     print("Error: Failed to get flight search URL")
            #     return
                
            # print(f"Flight search URL: {url}")
            
            # # Scrape flights
            # print("Scraping flights...")
            # flight_results = await scrape_flights(url)
            
            # if not flight_results:
            #     print("Error: Failed to scrape flights")
            #     return

            # --- v2 ---
            scraper = FlightScraperV2(
                args.origin,
                args.destination,
                args.num_guests
            )
            outbound_flights = await scraper.get_flight_details(args.start_date)
            outbound_flights_json = to_json(outbound_flights)
            outbound_flights_str = to_markdown(outbound_flights)

            return_flights = await scraper.get_flight_details(args.end_date)
            return_flights_json = to_json(return_flights)
            return_flights_str = to_markdown(return_flights)

            # Print results
            print("Outbound Flights:\n")
            print(outbound_flights_str)
            print("Return Flights:\n")
            print(return_flights_str)

            # Save results to file (pass the dict version)
            self._save_results_to_file('flight_results', {
                'outbound': outbound_flights_json,
                'return': return_flights_json
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def _search_hotels(self, args):
        try:
            print(f"Searching for hotels in {args.destination}...")
            
            # Get hotel search URL
            url = await get_hotel_search_url(
                args.destination, 
                args.start_date, 
                args.end_date, 
                args.num_guests
            )
            
            if not url:
                print("Error: Failed to get hotel search URL")
                return
                
            print(f"Hotel search URL: {url}")
            
            # Scrape hotels
            print("Scraping hotels...")
            hotel_results = await scrape_hotels(url)
            
            if not hotel_results:
                print("Error: Failed to scrape hotels")
                return
            
            # Print results (assuming hotel_results is already JSON serializable)
            print("\nHotel Results:")
            print(json.dumps(hotel_results, indent=2))
            
            # Save results to file
            self._save_results_to_file('hotel_results', hotel_results)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def _travel_summary(self, args):
        try:
            # Get flight and hotel results
            flight_results = self._get_file_or_string_content(args.flight_results)
            hotel_results = self._get_file_or_string_content(args.hotel_results)
            
            # Prepare model_dump equivalent
            model_data = {
                "start_date": args.start_date,
                "end_date": args.end_date,
                "num_guests": args.num_guests,
            }
            
            if hasattr(args, 'budget') and args.budget:
                model_data["budget"] = args.budget
            
            if hasattr(args, 'preferences') and args.preferences:
                model_data["preferences"] = args.preferences
            
            # Generate summary
            print("Generating travel summary...")
            result = get_travel_summary(
                flight_results,
                hotel_results,
                **model_data
            )
            
            # Print results
            print("\nTravel Summary:")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"Error: {str(e)}")

    async def _flights_hotels_summary(self, args):
        try:
            print(f"Searching for flights and hotels in {args.destination}...")

            # Scrape flights
            print("Scraping flights...")
            flight_results = await self._search_flights(args)
            if not flight_results:
                print("Error: Failed to scrape flights")
                return
            
            # Scrape hotels
            print("Scraping hotels...")
            hotel_results = await self._search_hotels(args)
            if not hotel_results:
                print("Error: Failed to scrape hotels")
                return
            
            # Generate summary
            print("Generating travel summary...")
            result = self._travel_summary(args)   
            
            # Save results to file
            self._save_results_to_file('flights_hotels_summary', result)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def _get_file_or_string_content(self, content):
        """Helper function to get content from a file path or string"""
        # First check if it's an absolute path
        if os.path.isabs(content) and os.path.exists(content):
            print(f"Loading content from absolute file path: {content}")
            with open(content, 'r') as f:
                return f.read()
        
        # Then check if it's a relative path to the script directory
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), content)
        if os.path.exists(path):
            print(f"Loading content from file: {path}")
            with open(path, 'r') as f:
                return f.read()
            
        # Then check if it's a relative path to the current working directory
        if os.path.exists(content):
            print(f"Loading content from relative file path: {content}")
            with open(content, 'r') as f:
                return f.read()
            
        # If not a file, return the content as is (assuming it's a JSON string)
        print("Content is not a file path, treating as raw data")
        return content
    
    def _save_results_to_file(self, filename, results):
        """Helper function to save results to a file"""
        # Create dumps directory if it doesn't exist
        dumps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dumps')
        if not os.path.exists(dumps_dir):
            os.makedirs(dumps_dir)
            
        # Save results to file in dumps directory
        filename = f"{filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(dumps_dir, filename)
        # Ensure results are JSON serializable before dumping
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {filepath}")
        except TypeError as e:
            print(f"\nError saving results to {filepath}: {e}")
            print("Attempting to save raw data...")
            # Fallback: try saving the raw representation if JSON fails
            with open(filepath.replace('.txt', '_raw.txt'), 'w') as f:
                f.write(str(results))
            print(f"Raw results saved to {filepath.replace('.txt', '_raw.txt')}")
            

if __name__ == '__main__':
    test_app = Debug()
    test_app.run() 