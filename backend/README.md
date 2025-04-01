# AI Travel Companion Backend

This is the FastAPI backend for the AI Travel Companion application.

## Setup

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the development server:

```bash
uvicorn main:app --reload
```

The server will start at http://localhost:8000

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc
