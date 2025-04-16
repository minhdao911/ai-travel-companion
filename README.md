# AI Travel Companion

An application leveraging AI to help users plan their travel, featuring a FastAPI backend powered by LangChain and LangGraph, and a Vue.js frontend.

### Demo

[Demo Video](https://github.com/user-attachments/assets/bfb33bc5-899b-412c-bbb2-9dafd9eb096a)

### Running the Application

#### Quick Start

Ensure the main run script is executable:

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

This script handles the setup and execution of both the backend API server and the frontend development server. The application will be available at http://localhost:5173, with the backend running on http://localhost:8000.

#### Manual Setup

If you prefer to run the frontend and backend separately, check out the setup in `backend` and `frontend` folders.

### AI Assistant Flow

The core of the backend is an AI assistant built using LangGraph. This allows for a stateful, agentic workflow where the AI can use tools to fulfill user requests.

The flow is visualized below:

![LangGraph Flow](https://github.com/user-attachments/assets/33fc7c1b-8a5d-4b11-9f5c-dc04759c96d0)

1.  **User Request**: The user sends a message via the frontend chat interface.
2.  **Assistant Node**: The request is processed by the main assistant node, which uses a language model (LLM) to understand the intent and decide the next step.
3.  **Tool Decision**: If the assistant determines it needs external information (like flight prices, hotel availability, or general web searches), it decides which tool(s) to use.
4.  **Tools Node**: The appropriate tool(s) (e.g., `search_flights`, `search_hotels`, `DuckDuckGoSearchRun`) are executed with the necessary parameters derived from the user request.
5.  **Tool Result**: The output from the tool is sent back to the assistant node.
6.  **Response Generation**: The assistant processes the tool results and generates a response for the user.
7.  **Streaming Response**: The response (including intermediate steps like tool usage) is streamed back to the frontend.

This cycle can repeat if multiple tool calls are needed to satisfy the user's request. The state (conversation history) is managed by LangGraph's checkpointer.

### Testing the Application

1.  Start the application using either the quick start or manual setup method.
2.  Visit http://localhost:5173 in your browser.
3.  Interact with the chat interface to ask for travel recommendations, flight/hotel searches, or general travel questions.
4.  Observe the streamed responses and potential tool usage indicators.

### Key Takeaways:

Integrating real-time flight and hotel data presented several challenges and led to iterative improvements:

- **Flight Data:**

  - **Initial Approach:** The first attempt involved using Playwright to automate interactions with Google Flights (generating the search URL based on user input) and then using Browser Use to scrape the resulting page.
  - **Challenges:** Automating Google pages with Playwright is quite unpredictable and prone to failures. Furthermore, the browser automation approach was slow due to the multi-step process, and the large context accumulated after each step significantly increased LLM request costs.
  - **Revised Approach:** After doing some research on the structure of Google Flights URLs, it's possible to construct these URLs directly from user input. There is a library called `fast-flights` which support this and then flight data can be extracted from the page content using parsing tools like BeautifulSoup or selectolax.
  - **Outcome:** This revised method is significantly faster, virtually cost-free (no LLM calls needed for scraping), and provides comparable flight data quality.

- **Hotel Data:**
  - **Challenges:** Constructing Google Hotels URLs directly is difficult due to numerous undocumented, encoded parameters likely used internally by Google. While Playwright could potentially fill the search form to get a results page URL, scraping the hotel results page is also challenging. HTML elements lack stable attributes, and CSS classes change frequently, making extraction brittle.
  - **Chosen Approach:** To balance cost, speed, and reliability, SERP API can be a reasonable option. BrightData SERP API are used for hotel searches.
  - **Limitations:** While functional, BrightData Google Hotels SERP API has many drawbacks. The documentation is lacking, the returned data is relatively basic (e.g., missing amenities and hotel details like check-in check-out time, etc.), and filtering options are limited.
  - **Mitigation & Future Work:** The assistant can supplement the basic hotel data using its web search tool. However, the initial data limitations might affect the quality of recommendations. Exploring alternative SERP APIs or refining scraping techniques could be future improvements.
