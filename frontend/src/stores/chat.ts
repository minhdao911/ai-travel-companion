import { type Message } from "@/types";
import { defineStore } from "pinia";

type Chat = {
  id: string;
  title: string;
  messages: Message[];
  loading: boolean;
};

// Create a factory function for message stores
export const createChatStore = (id: string) => {
  return defineStore(id, {
    state: () => ({
      chats: [] as Chat[],
    }),
    actions: {
      getChat(chatId: string) {
        return this.chats.find((c) => c.id === chatId);
      },
      addChat(chatId: string) {
        this.chats.unshift({
          id: chatId,
          title: "New Chat",
          messages: [],
          loading: false,
        });
      },
      updateChat(chatId: string, data: Partial<Chat>) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          Object.assign(chat, data);
        }
      },
      addMessage(chatId: string, message: Message) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          chat.messages.push(message);
        } else {
          this.chats.push({
            id: chatId,
            title: "New Chat",
            messages: [message],
            loading: false,
          });
        }
      },
      updateMessage(chatId: string, messageId: string, data: Partial<Message>) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          const index = chat.messages.findIndex((m) => m.id === messageId);
          if (index !== -1) {
            const chatMessage = chat.messages[index];
            chat.messages[index] = {
              ...chatMessage,
              ...data,
              status:
                data.status === "success" && chatMessage.status === "error" ? "error" : data.status,
            };
          }
        }
      },
      removeMessage(chatId: string, messageId: string) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          chat.messages = chat.messages.filter((m) => m.id !== messageId);
        }
      },
      clearMessages(chatId: string) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          chat.messages = [];
        }
      },
      setLoading(chatId: string, loading: boolean) {
        const chat = this.chats.find((c) => c.id === chatId);
        if (chat) {
          chat.loading = loading;
        }
      },
    },
  });
};

export const useChatStore = createChatStore("chat_store");
