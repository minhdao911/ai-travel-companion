# AI Travel Companion Backend

This is the FastAPI backend for the AI Travel Companion application.

### Setup

Ensure you have [Poetry](https://python-poetry.org/docs/#installation) installed.

Add environment variables:

```bash
OPEN_API_KEY=
# Helicone key for LLM model visibility (Optional)
HELICONE_API_KEY=
# BrightData vars for Google Hotels SERP API
BRIGHT_DATA_API_KEY=
BRIGHT_DATA_CUSTOMER_ID=
BRIGHT_DATA_API_ZONE=
```

Use the provided script for easy setup and execution:

**On macOS/Linux:**

```bash
cd backend
chmod +x run_backend.sh
./run_backend.sh
```

**On Windows:**

```bash
cd backend
run_backend.bat
```

These scripts automate the following steps:

1. Installing dependencies using `poetry install`.
2. Starting the FastAPI server using `poetry run uvicorn main:app --reload`.

Or follow these steps manually:

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies:

```bash
poetry install
```

3. Start the development server:

```bash
poetry run uvicorn main:app --reload
```

The server will start at http://localhost:8000.

### Debug Mode

The backend includes an interactive debug mode to test functions directly from the terminal without running the full server. This is useful for testing individual backend functions in isolation.

#### Running Debug Mode

##### On macOS/Linux:

```bash
chmod +x debug.sh
./debug.sh
```

##### On Windows:

```bash
debug.bat
```

#### Available Commands

In debug mode, you can test the following functions:

1. **health** - Check health of the API
2. **search-flights** - Search for flights
3. **search-hotels** - Search for hotels
4. **get-summary** - Get short summary based on input

#### Features

- **Interactive Interface**: Select commands from a menu and get prompted for required parameters
- **Retry Functionality**: After executing a command, you can:
  - Retry with the same parameters
  - Retry with new parameters
  - Return to the main menu
  - Exit the debug mode
- **Parameter Validation**: The debug mode validates parameter types and required fields
- **File Output**: Results from commands like search-flights and search-hotels are saved as text files in the `dumps` folder (created automatically if it doesn't exist)

#### Example Usage

To test flight search functionality:

1. Run the debug mode
2. Select "search-flights"
3. Enter required parameters (origin, destination, dates, etc.)
4. View the results
5. Choose to retry or return to the main menu

The flight search results will be saved to `backend/dumps/flight_results_[timestamp].txt`.

### API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc
