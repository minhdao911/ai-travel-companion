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
  Idle = "idle",
  Pending = "pending",
  Processing = "processing",
  Completed = "completed",
  Failed = "failed",
}

export enum TaskType {
  FlightSearch = "Flight Search",
  HotelSearch = "Hotel Search",
}

export type Task = {
  id?: string;
  type: TaskType;
  status: TaskStatus;
  messageId: string;
};

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  loading?: boolean;
  taskType?: TaskType;
};

export type TravelPreferences = {
  origin_airport_code?: string;
  destination_airport_code?: string;
  origin_city_name?: string;
  destination_city_name?: string;
  num_guests?: number;
  start_date?: string;
  end_date?: string;
  budget?: number;
  accommodation?: {
    type?: string;
    max_price_per_night?: number;
    amenities?: string[];
  };
  flight?: {
    class?: string;
    direct?: boolean;
  };
  activities?: string[];
  food_preferences?: string[];
};

export type TravelContext = {
  start_date?: string;
  end_date?: string;
  origin_city_name?: string;
  destination_city_name?: string;
  num_guests?: number;
  budget?: number;
  flights?: string;
  preferences?: string;
};
