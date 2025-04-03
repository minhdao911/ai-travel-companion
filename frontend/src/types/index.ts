export enum Tabs {
  FlightsAndHotels = "flightsAndHotels",
  Assistant = "assistant",
}

export type Message = {
  id: string;
  content: string;
  role: "user" | "assistant";
};
