import { type Message, MessageRole, TaskType } from "@/types";
import { defineStore } from "pinia";
import { generateId } from "@/utils/id";

// Create a factory function for message stores
export const createChatStore = (id: string) => {
  return defineStore(id, {
    state: () => ({
      messages: [] as Message[],
      loading: false,
    }),
    actions: {
      addMessage(message: Omit<Message, "id"> & { id?: string }) {
        this.messages.push({
          id: message.id || generateId(),
          ...message,
        });
      },
      updateMessage(id: string, data: Partial<Message>) {
        const index = this.messages.findIndex((m) => m.id === id);
        if (index !== -1) {
          this.messages[index] = { ...this.messages[index], ...data };
        }
      },
      removeMessage(id: string) {
        this.messages = this.messages.filter((m) => m.id !== id);
      },
      clearMessages() {
        this.messages = [];
      },
      setLoading(loading: boolean) {
        this.loading = loading;
      },
      resetChat() {
        this.clearMessages();
        this.setLoading(false);
      },
    },
  });
};

// Create specific store instances
export const useAgentChatStore = createChatStore("agentChat");
export const useAssistantChatStore = createChatStore("assistantChat");
