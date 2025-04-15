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

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  collapsable_content?: string;
  loading?: boolean;
  tool_calls?: Array<{ id: string; name: string; args: Record<string, any> }>;
  tool_call_id?: string;
};

export type SearchResults = {
  raw_data: string;
  json_data: Record<string, any>;
};
