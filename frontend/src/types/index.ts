export enum Tabs {
  FlightsAndHotels = "flightsAndHotels",
  Assistant = "assistant",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
}

export type Message = {
  id: string;
  content: string;
  role: MessageRole;
};
