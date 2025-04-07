<script setup lang="ts">
import { ref } from "vue";
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import { MessageRole, Tabs, TaskType } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";
import { getTravelDetails } from "@/services/api";
import { useTasks } from "@/composables/useTasks";
import { useTravelSearch } from "@/composables/useTravelSearch";
import { generateId } from "@/utils/id";
import { useTravelStore } from "@/stores/travel";
import { useAgentChatStore } from "@/stores/chat";
import { marked } from "marked";

const travelStore = useTravelStore();
const agentChatStore = useAgentChatStore();

const input = ref("");

// Initialize tasks system
const { setTaskProcessing, initializeTask, initializeTravelSummary } = useTasks(
  agentChatStore.setLoading,
  agentChatStore.addMessage,
  agentChatStore.updateMessage
);

// Initialize travel search with computed reference
const travelSearch = useTravelSearch(agentChatStore.addMessage, setTaskProcessing, initializeTask);

// Handle extracting travel details from user input
const processUserInput = async (userInput: string) => {
  try {
    agentChatStore.setLoading(true);

    // Create conversation history from existing messages
    const conversationHistory = agentChatStore.messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Send request to backend
    const responseData = await getTravelDetails(userInput, conversationHistory);

    // Store travel details if available
    if (responseData.complete && responseData.travel_preferences) {
      travelStore.setPreferences(responseData.travel_preferences);
      travelStore.setContext({
        start_date: responseData.travel_preferences.start_date,
        end_date: responseData.travel_preferences.end_date,
        origin_city_name: responseData.travel_preferences.origin_city_name,
        destination_city_name: responseData.travel_preferences.destination_city_name,
        num_guests: responseData.travel_preferences.num_guests,
        budget: responseData.travel_preferences.budget,
      });

      agentChatStore.addMessage({
        role: MessageRole.Assistant,
        content: await marked.parse(responseData.message),
        loading: false,
      });

      // Start flight search
      await travelSearch.startFlightSearch();

      return;
    }

    // Add the assistant's message with the formatted response
    agentChatStore.addMessage({
      role: MessageRole.Assistant,
      content: responseData.message,
    });
    agentChatStore.setLoading(false);
  } catch (error) {
    console.error("Error processing travel details:", error);
    agentChatStore.addMessage({
      role: MessageRole.Assistant,
      content: "Sorry, I encountered an error processing your travel plans. Please try again.",
    });
    agentChatStore.setLoading(false);
  }
};

const handleInputEnter = async () => {
  if (!input.value.trim() || agentChatStore.loading) return;

  // Add user message to chat
  agentChatStore.addMessage({
    role: MessageRole.User,
    content: input.value,
  });

  // Add loading message
  const loadingMessageId = generateId();
  agentChatStore.addMessage({
    id: loadingMessageId,
    content: "Thinking...",
    role: MessageRole.Assistant,
    loading: true,
  });

  const userInput = input.value;
  input.value = "";

  // Process the user input
  await processUserInput(userInput);

  // Remove loading message
  agentChatStore.removeMessage(loadingMessageId);
};

const checkIfTravelPlanComplete = (): boolean => {
  return !!(travelStore.context?.flight_results && travelStore.context?.hotel_results);
};

const handleTaskRegenerate = async (messageId: string) => {
  const message = agentChatStore.messages.find((msg) => msg.id === messageId);
  if (message) {
    switch (message.taskType) {
      case TaskType.FlightSearch:
        await travelSearch.startFlightSearch(checkIfTravelPlanComplete());
        break;
      case TaskType.HotelSearch:
        await travelSearch.startHotelSearch(checkIfTravelPlanComplete());
        break;
      case TaskType.TravelSummary:
        await initializeTravelSummary();
        break;
      default:
        break;
    }
  }
};
</script>

<template>
  <Container>
    <div class="flex flex-col justify-between w-full h-full">
      <Welcome v-if="agentChatStore.messages.length === 0">
        <p class="text-gray-500 max-w-xl text-center">
          I'm here to help you in planning your experience. Tell me your travel plan and preferences
          and I'll give you flights and hotel suggestions.
        </p>
      </Welcome>
      <div v-else class="flex flex-col w-full h-full overflow-y-auto">
        <ChatInterface
          :messages="agentChatStore.messages"
          :isLoading="agentChatStore.loading"
          :onRegenerate="handleTaskRegenerate"
        />
      </div>
      <TextInput
        placeholder="Where would you like to go?"
        :activeTab="Tabs.FlightsAndHotels"
        v-model="input"
        :onEnter="handleInputEnter"
        :disabled="agentChatStore.loading"
      />
    </div>
  </Container>
</template>
