import { ref, computed } from "vue";
import { useAgentChatStore } from "@/stores/chat";
import { streamRecommendation } from "@/services/api";
import { generateId } from "@/utils/common";
import { MessageRole } from "@/types";

/**
 * Composable for managing the travel planning chat interface using streaming.
 */
export function useChat() {
  const agentChatStore = useAgentChatStore();

  const input = ref("");
  const isLoading = ref(false);

  const handleInputEnter = async () => {
    if (!input.value.trim() || isLoading.value) return;

    const userInput = input.value;
    const userMessageId = generateId();
    input.value = "";

    agentChatStore.addMessage({
      id: userMessageId,
      role: MessageRole.User,
      content: userInput,
    });

    // Prepare conversation history
    const conversationHistory = agentChatStore.messages.map((msg) => ({
      role: msg.role,
      content: msg.content, // Send raw content
      ...(msg.role === MessageRole.Assistant && msg.tool_calls && { tool_calls: msg.tool_calls }),
      ...(msg.role === MessageRole.Assistant &&
        msg.tool_call_id && { tool_call_id: msg.tool_call_id }),
    }));

    // Add placeholder for assistant response
    const assistantMessageId = generateId();
    agentChatStore.addMessage({
      id: assistantMessageId,
      role: MessageRole.Assistant,
      content: "",
      loading: true,
    });
    isLoading.value = true;

    // --- Call Streaming API ---
    await streamRecommendation(conversationHistory, {
      onToken: async (token) => {
        // Find the message using store's messages array
        const existingMessage = agentChatStore.messages.find((m) => m.id === assistantMessageId);
        if (existingMessage) {
          const updatedContent = existingMessage.content + token;
          agentChatStore.updateMessage(assistantMessageId, {
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
        agentChatStore.updateMessage(assistantMessageId, {
          content: `Sorry, an error occurred: ${errorMessage}`,
          loading: false,
        });
        isLoading.value = false;
      },
      onEnd: () => {
        agentChatStore.updateMessage(assistantMessageId, {
          loading: false,
        });
        isLoading.value = false;
        console.log("Streaming finished.");
      },
    });
  };

  return {
    input,
    messages: computed(() => agentChatStore.messages),
    isLoading: computed(() => isLoading.value),
    handleInputEnter,
  };
}
