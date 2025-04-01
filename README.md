# AI Travel Companion

A web application with a FastAPI backend and Vue.js frontend for exploring travel destinations.

## Project Structure

- `frontend/`: Vue.js frontend with Tailwind CSS for styling
- `backend/`: FastAPI backend providing travel destination data

## Running the Application

### Quick Start (Recommended)

Make sure the script is executable:

```bash
chmod +x run_app.sh
```

Run the entire application (both frontend and backend) with a single command:

**On macOS/Linux:**

```bash
./run_app.sh
```

**On Windows:**

```bash
run_app.bat
```

This will start both the backend server and the frontend development server. The application will be available at http://localhost:5173

### Manual Setup

If you prefer to run the frontend and backend separately, follow these instructions:

#### Backend Setup

Make sure the script is executable:

```bash
cd backend
chmod +x run_backend.sh
```

Run the backend API server:

**On macOS/Linux:**

```bash
./run_backend.sh
```

**On Windows:**

```bash
run_backend.bat
```

The script includes the steps as follows:

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

You can view the API documentation at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

#### Frontend Setup

1. In a new terminal, navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Testing the Application

1. Visit http://localhost:5173 in your browser
2. Navigate to the "Destinations" page using the navigation menu
3. You should see destination cards loaded from the backend API

## API Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/destinations`: Get a list of travel destinations
