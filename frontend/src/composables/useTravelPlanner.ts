import { ref, computed } from "vue";
import { useAgentChatStore } from "@/stores/chat";
import { planTravel, getPlanStatus, type PlanStatusResponse } from "@/services/api";
import { generateId } from "@/utils/common";
import { type Message, MessageRole } from "@/types";
import { marked } from "marked";
import { usePolling } from "./usePolling"; // Import the usePolling composable
import { createMarkdownRenderder } from "@/utils/common";

// Define a type for the conversation history item
interface ConversationHistoryItem {
  role: MessageRole;
  content: string;
}

/**
 * Composable for managing the travel planning chat interface.
 */
export function useTravelPlanner() {
  const agentChatStore = useAgentChatStore();
  const input = ref("");
  const loadingMessageId = ref<string | null>(null);
  const optionalDetailsAsked = ref(false);

  // --- Marked Renderer Setup ---
  const renderer = createMarkdownRenderder();

  const parseMarkdown = async (content: string): Promise<string> => {
    return await marked.parse(content || "", { renderer });
  };

  // --- Polling Logic ---
  const handlePollingSuccess = async (response: PlanStatusResponse) => {
    console.log("Polling success:", response);
    agentChatStore.setLoading(false);
    if (loadingMessageId.value) {
      agentChatStore.removeMessage(loadingMessageId.value);
      loadingMessageId.value = null;
    }
    optionalDetailsAsked.value = response.data?.optional_details_asked || false;

    if (response.data?.assistant_message) {
      console.log("Backend asking for more info:", response.data.assistant_message);
      agentChatStore.addMessage({
        role: MessageRole.Assistant,
        content: await parseMarkdown(response.data.assistant_message),
        loading: false,
      });
    } else if (response.data?.final_summary) {
      console.log("Backend returned final summary.");
      agentChatStore.addMessage({
        role: MessageRole.Assistant,
        content: await parseMarkdown(response.data.final_summary),
      });
    } else {
      console.warn("Task completed but no assistant message or summary found.", response.data);
      agentChatStore.addMessage({
        role: MessageRole.Assistant,
        content:
          "I've finished processing, but couldn't generate a final plan. Please check the details provided.",
      });
    }
  };

  const handlePollingProcessing = (response: PlanStatusResponse) => {
    agentChatStore.setLoading(true);
    if (
      loadingMessageId.value &&
      !agentChatStore.messages.find((m) => m.id === loadingMessageId.value)
    ) {
      // Re-add loading message if it was removed prematurely
      agentChatStore.addMessage({
        id: loadingMessageId.value,
        content: "Thinking...",
        role: MessageRole.Assistant,
        loading: true,
      });
    } else if (loadingMessageId.value) {
      // Ensure loading state is true on the store if message exists
      agentChatStore.setLoading(true);
    }
  };

  const handlePollingError = (error: any) => {
    console.error("Task failed or polling error:", error);
    agentChatStore.setLoading(false);
    if (loadingMessageId.value) {
      agentChatStore.removeMessage(loadingMessageId.value);
      loadingMessageId.value = null;
    }
    const errorMessage =
      typeof error === "string" ? error : "An unknown error occurred during planning.";
    agentChatStore.addMessage({
      role: MessageRole.Assistant,
      content: `Sorry, I encountered an error: ${errorMessage}`,
      loading: false,
    });
  };

  const { startPolling, stopPolling, isPolling, currentTaskId } = usePolling<PlanStatusResponse>({
    pollFunction: getPlanStatus,
    onSuccess: handlePollingSuccess,
    onProcessing: handlePollingProcessing,
    onError: handlePollingError,
    pollInterval: 3000,
  });

  // --- Input Handling ---
  const handleInputEnter = async () => {
    if (!input.value.trim() || agentChatStore.loading || isPolling.value) return;

    const userInput = input.value;
    input.value = ""; // Clear input immediately

    agentChatStore.addMessage({
      role: MessageRole.User,
      content: userInput,
    });

    // Add loading message
    loadingMessageId.value = generateId();
    agentChatStore.addMessage({
      id: loadingMessageId.value,
      content: "Thinking...",
      role: MessageRole.Assistant,
      loading: true,
    });
    agentChatStore.setLoading(true);

    try {
      // Prepare conversation history (exclude loading message)
      const conversationHistory: ConversationHistoryItem[] = agentChatStore.messages
        .filter((msg): msg is Message & { id?: string } => msg.id !== loadingMessageId.value)
        .map((msg) => ({
          role: msg.role,
          content: (msg as any).rawContent || msg.content,
        }));

      const initialResponse = await planTravel(
        userInput,
        conversationHistory,
        optionalDetailsAsked.value
      );

      if (initialResponse.task_id) {
        startPolling(initialResponse.task_id);
      } else {
        // Handle case where task_id is missing but no error was thrown
        console.warn("planTravelV3 response missing task_id", initialResponse);
        handlePollingError("Sorry, I couldn't initiate the planning process.");
      }
    } catch (error) {
      console.error("Error processing input:", error);
      handlePollingError(
        "Sorry, I encountered an error starting the planning process. Please try again."
      );
      stopPolling(); // Ensure polling stops if the initial call fails
    }
  };

  return {
    input,
    messages: computed(() => agentChatStore.messages),
    isLoading: computed(() => agentChatStore.loading || isPolling.value),
    currentTaskId,
    handleInputEnter,
    // Regenerate function might need more context or specific implementation
    onRegenerate: () => {
      console.warn("Regenerate function not implemented in useTravelPlanner");
    },
  };
}
