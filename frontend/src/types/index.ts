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
  status?: "success" | "error" | "loading";
};

export type SearchResults = {
  raw_data: string;
  json_data: Record<string, any>;
};

export enum AIModelProvider {
  OpenAI = "openai",
  Google = "google",
}

export type AIModel = {
  id: string;
  name: string;
  provider: AIModelProvider;
};

export const availableModels: AIModel[] = [
  { id: "gpt-4.1", name: "GPT-4.1", provider: AIModelProvider.OpenAI },
  { id: "gpt-4.1-mini", name: "GPT-4.1 Mini", provider: AIModelProvider.OpenAI },
  { id: "o4-mini", name: "o4-mini", provider: AIModelProvider.OpenAI },
  { id: "o3-mini", name: "o3-mini", provider: AIModelProvider.OpenAI },
  {
    id: "gemini-2.5-flash-preview-04-17",
    name: "Gemini 2.5 Flash",
    provider: AIModelProvider.Google,
  },
  { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash", provider: AIModelProvider.Google },
  {
    id: "gemini-2.0-flash-lite",
    name: "Gemini 2.0 Flash-Lite",
    provider: AIModelProvider.Google,
  },
];
