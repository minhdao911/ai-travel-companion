export enum Tabs {
  FlightsAndHotels = "flightsAndHotels",
  Assistant = "assistant",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
  Task = "task",
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

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  loading?: boolean;
};

export type TravelPreferences = {
  origin_airport_code?: string;
  destination_airport_code?: string;
  origin_city_name: string;
  destination_city_name: string;
  num_guests: number;
  start_date: string;
  end_date: string;
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

export type Price = {
  amount: number;
  currency: string;
};

export type FlightDetails = {
  arrival_date: string;
  arrival_time: string;
  departure_date: string;
  departure_time: string;
  origin_city_name: string;
  destination_city_name: string;
  origin_airport_code: string;
  destination_airport_code: string;
  price: Price;
  num_stops: number;
  duration: string;
  airlines_and_flight_numbers: string;
  stop_locations: string;
};

export type TravelDetails = {
  flight: {
    outbound_flight: FlightDetails;
    return_flight: FlightDetails;
    total_price: Price;
  };
};
