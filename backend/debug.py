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
from tools.flight_scraper import FlightScraper, to_json, to_markdown
from tools.hotel_scraper import get_hotel_details


class Debug:
    def __init__(self):
        self.parser = self._create_parser()
        self.commands = {
            "search-flights": {
                "help": "Search for flights",
                "args": [
                    {
                        "name": "origin",
                        "type": str,
                        "required": True,
                        "help": "Origin airport code",
                    },
                    {
                        "name": "destination",
                        "type": str,
                        "required": True,
                        "help": "Destination airport code",
                    },
                    {
                        "name": "start_date",
                        "type": str,
                        "required": True,
                        "help": "Start date (YYYY-MM-DD)",
                    },
                    {
                        "name": "end_date",
                        "type": str,
                        "required": True,
                        "help": "End date (YYYY-MM-DD)",
                    },
                    {
                        "name": "num_guests",
                        "type": int,
                        "required": True,
                        "help": "Number of guests",
                    },
                    {
                        "name": "seat_class",
                        "type": str,
                        "required": False,
                        "help": "Seat class (optional)",
                    },
                    {
                        "name": "direct",
                        "type": bool,
                        "required": False,
                        "help": "Direct flight (optional)",
                    },
                ],
            },
            "search-hotels": {
                "help": "Search for hotels",
                "args": [
                    {
                        "name": "destination",
                        "type": str,
                        "required": True,
                        "help": "Destination city name",
                    },
                    {
                        "name": "start_date",
                        "type": str,
                        "required": True,
                        "help": "Start date (YYYY-MM-DD)",
                    },
                    {
                        "name": "end_date",
                        "type": str,
                        "required": True,
                        "help": "End date (YYYY-MM-DD)",
                    },
                    {
                        "name": "num_guests",
                        "type": int,
                        "required": True,
                        "help": "Number of guests",
                    },
                    {
                        "name": "currency",
                        "type": str,
                        "required": False,
                        "help": "Currency code: USD, EUR, GBP, etc. (optional)",
                    },
                    {
                        "name": "free_cancellation",
                        "type": bool,
                        "required": False,
                        "help": "Free cancellation (optional)",
                    },
                    {
                        "name": "accommodation_types",
                        "type": str,
                        "required": False,
                        "help": "List of accommodation types, separated by commas (optional)",
                    },
                ],
            },
        }

    def _run_command(self, cmd_name, args):
        try:
            namespace = argparse.Namespace(**args)
            if cmd_name == "health":
                self._health_check()
            elif cmd_name == "search-flights":
                asyncio.run(self._search_flights(namespace))
            elif cmd_name == "search-hotels":
                asyncio.run(self._search_hotels(namespace))
        except Exception as e:
            print(f"\nCommand execution failed: {str(e)}")

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Test AI Travel Companion Backend Functions"
        )
        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # Debug mode command
        debug_parser = subparsers.add_parser(
            "debug", help="Run in interactive debug mode"
        )

        # Health check command
        health_parser = subparsers.add_parser("health", help="Check health of the API")

        # Search flights command
        flights_parser = subparsers.add_parser(
            "search-flights", help="Search for flights"
        )
        flights_parser.add_argument(
            "--origin", type=str, required=True, help="Origin city name"
        )
        flights_parser.add_argument(
            "--destination", type=str, required=True, help="Destination city name"
        )
        flights_parser.add_argument(
            "--start-date", type=str, required=True, help="Start date (YYYY-MM-DD)"
        )
        flights_parser.add_argument(
            "--end-date", type=str, required=True, help="End date (YYYY-MM-DD)"
        )
        flights_parser.add_argument(
            "--num-guests", type=int, required=True, help="Number of guests"
        )
        flights_parser.add_argument(
            "--seat-class", type=str, help="Seat class (optional)"
        )
        flights_parser.add_argument(
            "--direct", type=bool, help="Direct flight (optional)"
        )

        # Search hotels command
        hotels_parser = subparsers.add_parser("search-hotels", help="Search for hotels")
        hotels_parser.add_argument(
            "--destination", type=str, required=True, help="Destination city name"
        )
        hotels_parser.add_argument(
            "--start-date", type=str, required=True, help="Start date (YYYY-MM-DD)"
        )
        hotels_parser.add_argument(
            "--end-date", type=str, required=True, help="End date (YYYY-MM-DD)"
        )
        hotels_parser.add_argument(
            "--num-guests", type=int, required=True, help="Number of guests"
        )
        hotels_parser.add_argument(
            "--currency", type=str, help="Currency code: USD, EUR, GBP, etc. (optional)"
        )
        hotels_parser.add_argument(
            "--accommodation-types",
            type=str,
            help="List of accommodation types, separated by commas (optional)",
        )

        # List available commands
        list_parser = subparsers.add_parser("list", help="List available commands")

        return parser

    def run(self, args=None):
        args = self.parser.parse_args(args)

        if args.command == "debug":
            self._run_debug_mode()
            return

        if not args.command or args.command == "list":
            self.parser.print_help()
            return

        self._run_command(args.command, args)

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
            if choice == "0":
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
            if (
                previous_args
                and input("Use same arguments as before? (y/n): ").lower() == "y"
            ):
                args = previous_args
            else:
                # Prompt for new arguments
                args = {}
                for arg in cmd_details["args"]:
                    while True:
                        prompt = f"{arg['name']} ({arg['help']}): "
                        if not arg["required"]:
                            prompt += "(optional, press Enter to skip) "

                        value = input(prompt)

                        # Skip optional arguments if no value provided
                        if not value and not arg["required"]:
                            break

                        # Validate required arguments
                        if not value and arg["required"]:
                            print(
                                f"Error: {arg['name']} is required. Please provide a value."
                            )
                            continue

                        # Convert value to appropriate type
                        try:
                            if arg["type"] == int:
                                value = int(value)
                            args[arg["name"]] = value
                            break
                        except ValueError:
                            print(
                                f"Error: {arg['name']} must be a {arg['type'].__name__}. Please try again."
                            )

                # Save arguments for potential reuse
                previous_args = args.copy()

            # Execute command
            self._run_command(cmd_name, args)

            # Ask if user wants to retry the command
            retry_choice = input(
                "\nDo you want to: [r]etry, [m]ain menu, or [q]uit? (r/m/q): "
            ).lower()
            if retry_choice == "r":
                retry = True
            elif retry_choice == "q":
                print("Exiting debug mode...")
                sys.exit(0)
            else:
                retry = False

    def _health_check(self):
        print(json.dumps({"status": "ok", "message": "API is running"}, indent=2))

    async def _search_flights(self, args):
        try:
            print(f"Searching for flights from {args.origin} to {args.destination}...")

            print(args)

            # Safely access optional arguments with default values
            seat_class = getattr(args, "seat_class", "economy")
            direct = getattr(args, "direct", False)

            scraper = FlightScraper(
                args.origin,
                args.destination,
                args.num_guests,
                seat_class,
                direct,
            )
            outbound_flights = scraper.get_flight_details(args.start_date)
            outbound_flights_json = to_json(outbound_flights)
            outbound_flights_str = to_markdown(outbound_flights)

            return_flights = scraper.get_flight_details(args.end_date)
            return_flights_json = to_json(return_flights)
            return_flights_str = to_markdown(return_flights)

            # Print results
            print("Outbound Flights:\n")
            print(outbound_flights_str)
            print("Return Flights:\n")
            print(return_flights_str)

            # Save results to file (pass the dict version)
            self._save_results_to_file(
                "flight_results",
                {"outbound": outbound_flights_json, "return": return_flights_json},
            )

        except Exception as e:
            print(f"Error: {str(e)}")

    async def _search_hotels(self, args):
        try:
            print(f"Searching for hotels in {args.destination}...")

            results = get_hotel_details(
                args.destination,
                args.start_date,
                args.end_date,
                args.num_guests,
                args.currency,
                args.free_cancellation,
                args.accommodation_types,
            )

            # Save results to file
            self._save_results_to_file("hotel_results", results)

        except Exception as e:
            print(f"Error: {str(e)}")

    def _get_file_or_string_content(self, content):
        """Helper function to get content from a file path or string"""
        # First check if it's an absolute path
        if os.path.isabs(content) and os.path.exists(content):
            print(f"Loading content from absolute file path: {content}")
            with open(content, "r") as f:
                return f.read()

        # Then check if it's a relative path to the script directory
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), content)
        if os.path.exists(path):
            print(f"Loading content from file: {path}")
            with open(path, "r") as f:
                return f.read()

        # Then check if it's a relative path to the current working directory
        if os.path.exists(content):
            print(f"Loading content from relative file path: {content}")
            with open(content, "r") as f:
                return f.read()

        # If not a file, return the content as is (assuming it's a JSON string)
        print("Content is not a file path, treating as raw data")
        return content

    def _save_results_to_file(self, filename, results):
        """Helper function to save results to a file"""
        # Create dumps directory if it doesn't exist
        dumps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dumps")
        if not os.path.exists(dumps_dir):
            os.makedirs(dumps_dir)

        # Save results to file in dumps directory
        filename = f"{filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(dumps_dir, filename)
        # Ensure results are JSON serializable before dumping
        try:
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {filepath}")
        except TypeError as e:
            print(f"\nError saving results to {filepath}: {e}")
            print("Attempting to save raw data...")
            # Fallback: try saving the raw representation if JSON fails
            with open(filepath.replace(".txt", "_raw.txt"), "w") as f:
                f.write(str(results))
            print(f"Raw results saved to {filepath.replace('.txt', '_raw.txt')}")


if __name__ == "__main__":
    test_app = Debug()
    test_app.run()
