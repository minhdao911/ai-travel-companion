import { TaskType, MessageRole, type Message } from "@/types";
import { searchFlights, searchHotels } from "@/services/api";
import { generateId } from "@/utils/id";
import { useTravelStore } from "@/stores/travel";

export function useTravelSearch(
  addMessage: (message: Omit<Message, "id">) => void,
  setTaskProcessing: (taskType: TaskType, taskId: string) => void,
  initializeTask: (taskType: TaskType, message: Message, regenerate?: boolean) => string
) {
  const travelStore = useTravelStore();

  // Start flight search
  const startFlightSearch = async (regenerate?: boolean) => {
    const preferences = travelStore.preferences;
    if (!preferences) {
      console.error("Cannot start flight search: Travel details are missing");
      return;
    }

    try {
      // Create task message with progress
      initializeTask(
        TaskType.FlightSearch,
        {
          id: generateId(),
          content: "🛫 Finding available flights for your dates...",
          role: MessageRole.Info,
          loading: true,
        },
        regenerate
      );

      // Call the flight search API
      const response = await searchFlights(preferences);
      console.log("Flight search response", response);

      // Store the task ID and update status
      setTaskProcessing(TaskType.FlightSearch, response.task_id);

      return response.task_id;
    } catch (e) {
      console.error("Error starting flight search:", e);
      addMessage({
        content: "Failed to start flight search. Please try again.",
        role: MessageRole.Task,
        taskType: TaskType.FlightSearch,
      });
      return null;
    }
  };

  // Start hotel search
  const startHotelSearch = async (regenerate?: boolean) => {
    const preferences = travelStore.preferences;
    if (!preferences) {
      console.error("Cannot start hotel search: Travel details are missing");
      return;
    }

    try {
      // Create task message with progress
      initializeTask(
        TaskType.HotelSearch,
        {
          id: generateId(),
          content: "🏨 Finding hotels for your stay...",
          role: MessageRole.Info,
          loading: true,
        },
        regenerate
      );

      // Call the hotel search API
      const response = await searchHotels(preferences);
      console.log("Hotel search response", response);

      // Store the task ID
      setTaskProcessing(TaskType.HotelSearch, response.task_id);

      return response.task_id;
    } catch (e) {
      console.error("Error starting hotel search:", e);
      addMessage({
        content: "Failed to start hotel search. Please try again.",
        role: MessageRole.Task,
        taskType: TaskType.HotelSearch,
      });
      return null;
    }
  };

  return {
    startFlightSearch,
    startHotelSearch,
  };
}
