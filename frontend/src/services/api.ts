import axios from "axios";
import type { Message, TravelContext, TravelPreferences } from "@/types";

const API_URL = import.meta.env.VITE_API_URL;

// Function to extract travel details from user input
export const getTravelDetails = async (
  userInput: string,
  conversationHistory: Pick<Message, "role" | "content">[]
) => {
  const response = await axios.post(`${API_URL}/api/travel-details`, {
    user_input: userInput,
    conversation_history: conversationHistory,
  });
  return response.data;
};

// Function to get travel summary
export const getTravelSummary = async (context: TravelContext) => {
  const response = await axios.post(`${API_URL}/api/travel-summary`, {
    ...context,
    budget: context.budget || undefined,
  });
  return response.data;
};

// Function to search for flights
export const searchFlights = async (preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/search-flights`, {
    origin_city_name: preferences.origin_city_name,
    destination_city_name: preferences.destination_city_name,
    start_date: preferences.start_date,
    end_date: preferences.end_date,
    num_guests: preferences.num_guests,
  });
  return response.data;
};

// Function to search for hotels
export const searchHotels = async (preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/search-hotels`, {
    destination_city_name: preferences.destination_city_name,
    start_date: preferences.start_date,
    end_date: preferences.end_date,
    num_guests: preferences.num_guests,
  });
  return response.data;
};

// Function to check task status
export const checkTaskStatus = async (taskId: string) => {
  const response = await axios.get(`${API_URL}/api/task-status/${taskId}`);
  return response.data;
};
