<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from "vue";
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import { MessageRole, Tabs } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";
import { getTravelDetails } from "@/services/api";
import { useChat } from "@/composables/useChat";
import { useTasks } from "@/composables/useTasks";
import { useTravelSearch } from "@/composables/useTravelSearch";
import { generateId } from "@/utils/id";

// Initialize composables
const {
  messages,
  travelPreferences,
  isLoading,
  addMessage,
  updateMessage,
  setTravelPreferences,
  createUserMessage,
  createAssistantMessage,
  clearChatState,
} = useChat();

// Initialize tasks system
const { startPolling, setTaskProcessing, addTaskMessage } = useTasks(addMessage, updateMessage);

// Initialize travel search with computed reference
const travelSearch = useTravelSearch(
  computed(() => travelPreferences.value),
  addMessage,
  setTaskProcessing,
  addTaskMessage
);

const input = ref("");

// Handle extracting travel details from user input
const processUserInput = async (userInput: string) => {
  try {
    isLoading.value = true;

    // Create conversation history from existing messages
    const conversationHistory = messages.value.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Send request to backend
    const responseData = await getTravelDetails(userInput, conversationHistory);

    // Store travel details if available
    if (responseData.complete && responseData.travel_preferences) {
      setTravelPreferences(responseData.travel_preferences);

      addMessage(createAssistantMessage(responseData.message));

      // Start flight search
      await travelSearch.startFlightSearch();
      startPolling();

      return;
    }

    // Add the assistant's message with the formatted response
    addMessage(createAssistantMessage(responseData.message));
    isLoading.value = false;
  } catch (error) {
    console.error("Error processing travel details:", error);
    addMessage(
      createAssistantMessage(
        "Sorry, I encountered an error processing your travel plans. Please try again."
      )
    );
    isLoading.value = false;
  }
};

const handleInputEnter = async () => {
  if (!input.value.trim() || isLoading.value) return;

  // Add user message to chat
  addMessage(createUserMessage(input.value));

  // Add loading message
  const loadingMessageId = generateId();
  addMessage({
    id: loadingMessageId,
    content: "Thinking...",
    role: MessageRole.Assistant,
  });

  const userInput = input.value;
  input.value = "";

  // Process the user input
  await processUserInput(userInput);

  // Remove loading message
  messages.value = messages.value.filter((msg) => msg.id !== loadingMessageId);
};

// Set up event listener when component is mounted
onMounted(() => {
  window.addEventListener("clear-chat-state", clearChatState);
});

// Clean up event listener when component is unmounted
onUnmounted(() => {
  window.removeEventListener("clear-chat-state", clearChatState);
});
</script>

<template>
  <Container>
    <div class="flex flex-col justify-between w-full h-full">
      <Welcome v-if="messages.length === 0">
        <p class="text-gray-500 max-w-xl text-center">
          I'm here to help you in planning your experience. Tell me your travel plan and preferences
          and I'll give you flights and hotel suggestions.
        </p>
      </Welcome>
      <div v-else class="flex flex-col w-full h-full overflow-y-auto">
        <ChatInterface :messages="messages" />
      </div>
      <TextInput
        placeholder="Where would you like to go?"
        :activeTab="Tabs.FlightsAndHotels"
        v-model="input"
        :onEnter="handleInputEnter"
        :disabled="isLoading"
      />
    </div>
  </Container>
</template>
