import { TaskType } from "@/types";

export function formatTaskType(taskType: TaskType): string {
  switch (taskType) {
    case TaskType.FlightSearch:
      return "Flight search";
    case TaskType.HotelSearch:
      return "Hotel search";
    default:
      return taskType;
  }
}
