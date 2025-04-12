export enum Tabs {
  FlightsAndHotels = "flightsAndHotels",
  Assistant = "assistant",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
  Task = "task",
  Info = "info",
}

export enum TaskStatus {
  Pending = "pending",
  Processing = "processing",
  Completed = "completed",
  Failed = "failed",
}

export enum TaskType {
  FlightSearch = "flight_search",
  HotelSearch = "hotel_search",
  TravelSummary = "travel_summary",
  TravelDetails = "travel_details",
}

export type Task = {
  id?: string;
  type: TaskType;
  status: TaskStatus;
  messageId: string;
  regenerate?: boolean;
};

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  collapsable_content?: string;
  taskType?: TaskType;
  loading?: boolean;
};

export type TravelPreferences = {
  accommodation?: {
    types?: string[];
    max_price_per_night?: number;
    amenities?: string[];
  };
  flight?: {
    class?: "economy" | "premium economy" | "business" | "first";
    direct?: boolean;
  };
  activities?: string[];
  food_preferences?: string[];
};

export type TravelContext = {
  start_date: string;
  end_date: string;
  origin_city_name: string;
  destination_city_name: string;
  origin_airport_code: string;
  destination_airport_code: string;
  num_guests: number;
  budget?: number;
  currency?: string;
  flight_results?: string;
  hotel_results?: string;
  summary?: string;
};
