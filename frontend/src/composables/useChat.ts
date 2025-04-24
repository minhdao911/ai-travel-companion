import { ref, computed } from "vue";
import type { Ref } from "vue";
import { useChatStore } from "@/stores/chat";
import { streamChat } from "@/services/api";
import { v4 as uuidv4 } from "uuid";
import { MessageRole, type AIModel, type Message } from "@/types";

/**
 * Composable for managing the travel planning chat interface using streaming.
 */
export function useChat(chatId: Ref<string>, selectedModel: Ref<AIModel>) {
  const chatStore = useChatStore();

  const input = ref("");
  const isLoading = ref(false);

  const stream = async (messages: Message[], assistantMessageId: string) => {
    const conversationHistory = messages.map((msg) => ({
      role: msg.role,
      content: msg.content, // Send raw content
    }));
    isLoading.value = true;

    console.log("Streaming started...");
    // --- Call Streaming API ---
    await streamChat(conversationHistory, {
      onToken: async (token) => {
        // Find the message using store's messages array
        const existingMessage = messages.find((m) => m.id === assistantMessageId);
        if (existingMessage) {
          const updatedContent = existingMessage.content + token;
          chatStore.updateMessage(chatId.value, assistantMessageId, {
            content: updatedContent,
            status: "loading",
          });
        }
      },
      onToolCallChunk: (chunk) => {},
      onToolStart: (name, input) => {
        console.log(`Starting tool: ${name}`, input);
      },
      onToolEnd: (name) => {
        console.log(`Tool finished: ${name}`);
      },
      onError: (errorMessage) => {
        console.error("Streaming Error:", errorMessage);
        chatStore.updateMessage(chatId.value, assistantMessageId, {
          content: `Sorry, an error occurred: ${errorMessage}`,
          status: "error",
        });
        isLoading.value = false;
      },
      onEnd: () => {
        chatStore.updateMessage(chatId.value, assistantMessageId, {
          status: "success",
        });
        isLoading.value = false;
        console.log("Streaming finished.");
      },
      model: selectedModel.value,
    });
  };

  const handleInputEnter = async () => {
    if (!input.value.trim() || isLoading.value) return;

    const userInput = input.value;
    const userMessageId = uuidv4();
    input.value = "";

    chatStore.addMessage(chatId.value, {
      id: userMessageId,
      role: MessageRole.User,
      content: userInput,
    });

    // Prepare conversation history
    const messages = chatStore.getChat(chatId.value)?.messages || [];

    // Add placeholder for assistant response
    const assistantMessageId = uuidv4();
    chatStore.addMessage(chatId.value, {
      id: assistantMessageId,
      role: MessageRole.Assistant,
      content: "",
      status: "loading",
    });

    await stream(messages, assistantMessageId);
  };

  return {
    input,
    messages: computed(() => chatStore.getChat(chatId.value)?.messages || []),
    isLoading: computed(() => isLoading.value),
    handleInputEnter,
    stream,
  };
}
