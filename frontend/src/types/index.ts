export enum Tabs {
  FlightsAndHotels = "flightsAndHotels",
  Assistant = "assistant",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
}

export enum TaskStatus {
  Pending = "pending",
  Processing = "processing",
  Completed = "completed",
  Failed = "failed",
}

export type Message = {
  id: string;
  content: string;
  role: MessageRole;
};

export type TravelDetails = {
  /** The 3-letter airport code for departure */
  origin_airport_code?: string;
  /** The 3-letter airport code for arrival */
  destination_airport_code?: string;
  /** The name of the departure city */
  origin_city_name: string;
  /** The name of the destination city */
  destination_city_name: string;
  /** Number of travelers */
  num_guests: number;
  /** Departure date in format like May 2, 2025 */
  start_date: string;
  /** Return date in format like May 9, 2025 */
  end_date: string;
  /** Total budget for the trip in USD */
  budget?: number;
  /** Accommodation preferences */
  accommodation?: {
    /** Type of accommodation (hotel, hostel, etc.) */
    type?: string;
    /** Maximum price per night in USD */
    max_price_per_night?: number;
    /** List of desired amenities */
    amenities?: string[];
  };
  /** Flight preferences */
  flight?: {
    /** Flight class (economy, business, first) */
    class?: string;
    /** Whether direct flights are preferred */
    direct?: boolean;
  };
  /** List of desired activities */
  activities?: string[];
  /** List of food preferences */
  food_preferences?: string[];
};
