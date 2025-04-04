import { ref } from "vue";
import { MessageRole, type Message, type TravelDetails } from "@/types";
import { generateId } from "@/services/id";

export function useChat() {
  const messages = ref<Message[]>([]);
  const travelDetails = ref<TravelDetails | null>(null);
  const isLoading = ref(false);

  // Add a new message to the chat
  const addMessage = (message: Message) => {
    messages.value.push(message);
  };

  const updateMessage = (id: string, data: Partial<Message>) => {
    const index = messages.value.findIndex((m) => m.id === id);
    if (index !== -1) {
      messages.value[index] = { ...messages.value[index], ...data };
    }
  };

  // Set travel details
  const setTravelDetails = (details: TravelDetails) => {
    travelDetails.value = details;
  };

  // Create a user message
  const createUserMessage = (content: string): Message => {
    return {
      id: generateId(),
      content,
      role: MessageRole.User,
    };
  };

  // Create an assistant message
  const createAssistantMessage = (content: string): Message => {
    return {
      id: generateId(),
      content,
      role: MessageRole.Assistant,
    };
  };

  // Create a task message
  const createTaskMessage = (content: string): Message => {
    return {
      id: generateId(),
      content,
      role: MessageRole.Task,
    };
  };

  // Clear all chat state
  const clearChatState = () => {
    messages.value = [];
    travelDetails.value = null;
    isLoading.value = false;
  };

  return {
    messages,
    travelDetails,
    isLoading,
    addMessage,
    updateMessage,
    setTravelDetails,
    createUserMessage,
    createAssistantMessage,
    createTaskMessage,
    clearChatState,
  };
}
