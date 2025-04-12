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
export const getTravelSummary = async (context: TravelContext, preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/travel-summary`, {
    ...context,
    preferences,
  });
  return response.data;
};

// Function to search for flights
export const searchFlights = async (context: TravelContext, preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/search-flights`, {
    origin_city_name: context.origin_city_name,
    destination_city_name: context.destination_city_name,
    start_date: context.start_date,
    end_date: context.end_date,
    num_guests: context.num_guests,
    preferences: preferences.flight,
  });
  return response.data;
};

export const searchFlightsV2 = async (context: TravelContext, preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/v2/search-flights`, {
    origin_airport_code: context.origin_airport_code,
    destination_airport_code: context.destination_airport_code,
    start_date: context.start_date,
    end_date: context.end_date,
    num_guests: context.num_guests,
    preferences: preferences.flight,
  });
  return response.data;
};

// Function to search for hotels
export const searchHotels = async (context: TravelContext, preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/search-hotels`, {
    destination_city_name: context.destination_city_name,
    start_date: context.start_date,
    end_date: context.end_date,
    num_guests: context.num_guests,
    preferences: preferences.accommodation,
  });
  return response.data;
};

export const searchHotelsV2 = async (context: TravelContext, preferences: TravelPreferences) => {
  const response = await axios.post(`${API_URL}/api/v2/search-hotels`, {
    destination_city_name: context.destination_city_name,
    start_date: context.start_date,
    end_date: context.end_date,
    num_guests: context.num_guests,
    currency: context.currency,
    preferences: preferences.accommodation,
  });
  return response.data;
};

// Function to check task status
export const checkTaskStatus = async (taskId: string) => {
  const response = await axios.get(`${API_URL}/api/task-status/${taskId}`);
  return response.data;
};
