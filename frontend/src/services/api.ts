import axios from "axios";
import type { Message, TravelState } from "@/types";

const API_URL = import.meta.env.VITE_API_URL;

interface PlanTravelRequest {
  user_input: string;
  conversation_history: Pick<Message, "role" | "content">[];
  optional_details_asked: boolean;
}

interface PlanTravelResponse {
  task_id: string;
  status: string; // Should be "PENDING" initially
}

export interface PlanStatusResponse {
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  data?: TravelState; // The final state of the graph
  error?: string; // Top-level error message if the task failed critically
}

/**
 * Initiates the travel planning process using the LangGraph backend.
 */
export const planTravel = async (
  userInput: string,
  conversationHistory: Pick<Message, "role" | "content">[],
  optionalDetailsAsked: boolean
): Promise<PlanTravelResponse> => {
  const response = await axios.post<PlanTravelResponse>(
    `${API_URL}/api/travel-recommendation`,
    {
      user_input: userInput,
      conversation_history: conversationHistory,
      optional_details_asked: optionalDetailsAsked,
    } satisfies PlanTravelRequest // Ensure request body matches backend expectation
  );
  return response.data;
};

/**
 * Gets the status and result of a travel planning task.
 */
export const getPlanStatus = async (taskId: string): Promise<PlanStatusResponse> => {
  const response = await axios.get<PlanStatusResponse>(
    `${API_URL}/api/travel-recommendation/status/${taskId}`
  );
  return response.data;
};
