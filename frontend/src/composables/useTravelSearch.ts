import {
  TaskType,
  MessageRole,
  type Message,
  type TravelDetails,
  type TravelPreferences,
} from "@/types";
import { searchFlights, searchHotels } from "@/services/api";
import type { ComputedRef } from "vue";
import { generateId } from "@/utils/id";

export function useTravelSearch(
  travelPreferences: ComputedRef<TravelPreferences | null>,
  addMessage: (message: Message) => void,
  setTaskProcessing: (taskType: TaskType, taskId: string) => void,
  addTaskMessage: (taskType: TaskType, message: Message) => string
) {
  // Start flight search
  const startFlightSearch = async () => {
    const preferences = travelPreferences.value;
    if (!preferences) {
      console.error("Cannot start flight search: Travel details are missing");
      return;
    }

    try {
      // Create task message with progress
      addTaskMessage(TaskType.FlightSearch, {
        id: generateId(),
        content: "✈️  Finding available flights for your dates..",
        role: MessageRole.Task,
      });

      // Call the flight search API
      const response = await searchFlights(preferences);

      // Store the task ID and update status
      setTaskProcessing(TaskType.FlightSearch, response.task_id);

      return response.task_id;
    } catch (e) {
      console.error("Error starting flight search:", e);
      addMessage({
        id: generateId(),
        content: "Failed to start flight search. Please try again.",
        role: MessageRole.Assistant,
      });
      return null;
    }
  };

  // Start hotel search
  const startHotelSearch = async () => {
    const preferences = travelPreferences.value;
    if (!preferences) {
      console.error("Cannot start hotel search: Travel details are missing");
      return;
    }

    try {
      // Create task message with progress
      addTaskMessage(TaskType.HotelSearch, {
        id: generateId(),
        content: "🏨 Finding hotels for your stay...",
        role: MessageRole.Task,
      });

      // Call the hotel search API
      const response = await searchHotels(preferences);

      // Store the task ID
      setTaskProcessing(TaskType.HotelSearch, response.task_id);

      return response.task_id;
    } catch (e) {
      console.error("Error starting hotel search:", e);
      addMessage({
        id: generateId(),
        content: "Failed to start hotel search. Please try again.",
        role: MessageRole.Assistant,
      });
      return null;
    }
  };

  return {
    startFlightSearch,
    startHotelSearch,
  };
}
