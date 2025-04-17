import { ref, computed } from "vue";
import type { Ref } from "vue";
import { useChatStore } from "@/stores/chat";
import { streamChat } from "@/services/api";
import { v4 as uuidv4 } from "uuid";
import { MessageRole } from "@/types";

/**
 * Composable for managing the travel planning chat interface using streaming.
 */
export function useChat(chatId: Ref<string>) {
  const chatStore = useChatStore();

  const input = ref("");
  const isLoading = ref(false);

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
    const conversationHistory = messages.map((msg) => ({
      role: msg.role,
      content: msg.content, // Send raw content
      ...(msg.role === MessageRole.Assistant && msg.tool_calls && { tool_calls: msg.tool_calls }),
      ...(msg.role === MessageRole.Assistant &&
        msg.tool_call_id && { tool_call_id: msg.tool_call_id }),
    }));

    // Add placeholder for assistant response
    const assistantMessageId = uuidv4();
    chatStore.addMessage(chatId.value, {
      id: assistantMessageId,
      role: MessageRole.Assistant,
      content: "",
      loading: true,
    });
    isLoading.value = true;

    // --- Call Streaming API ---
    await streamChat(conversationHistory, {
      onToken: async (token) => {
        // Find the message using store's messages array
        const existingMessage = messages.find((m) => m.id === assistantMessageId);
        if (existingMessage) {
          const updatedContent = existingMessage.content + token;
          chatStore.updateMessage(chatId.value, assistantMessageId, {
            content: updatedContent,
            loading: true,
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
          loading: false,
        });
        isLoading.value = false;
      },
      onEnd: () => {
        chatStore.updateMessage(chatId.value, assistantMessageId, {
          loading: false,
        });
        isLoading.value = false;
        console.log("Streaming finished.");
      },
    });
  };

  return {
    input,
    messages: computed(() => chatStore.getChat(chatId.value)?.messages || []),
    isLoading: computed(() => isLoading.value),
    handleInputEnter,
  };
}
