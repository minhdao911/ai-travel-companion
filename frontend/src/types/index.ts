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
  Pending = "PENDING",
  Processing = "PROCESSING",
  Completed = "COMPLETED",
  Failed = "FAILED",
}

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  collapsable_content?: string;
  loading?: boolean;
};

export type SearchResults = {
  raw_data: string;
  json_data: Record<string, any>;
};

export type TravelDetails = {
  start_date: string;
  end_date: string;
  origin_city_name: string;
  destination_city_name: string;
  origin_airport_code: string;
  destination_airport_code: string;
  num_guests: number;
  budget?: number;
  currency?: string;
  accommodation?: {
    types?: string[];
    max_price_per_night?: number;
    amenities?: string[];
    free_cancellation?: boolean;
  };
  flight?: {
    class?: "economy" | "premium economy" | "business" | "first";
    direct?: boolean;
  };
  activities?: string[];
  food_preferences?: string[];
};

export type TravelState = {
  conversation_history: Pick<Message, "role" | "content">[];
  user_input?: string;
  extracted_details?: TravelDetails;
  flight_search_results?: SearchResults;
  hotel_search_results?: SearchResults;
  final_summary?: string;
  error_message?: string;
  assistant_message?: string;
  optional_details_asked?: boolean;
};
