<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import { MessageRole, Tabs, type Message, type TravelDetails } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";
import FlightSearch from "@/components/FlightSearch.vue";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

const messages = ref<Message[]>([]);
const input = ref("");
const isLoading = ref(false);
const travelDetails = ref<TravelDetails | null>(null);
const showFlightSearch = ref(false);

// Generate unique message IDs
const generateMessageId = () => {
  return Date.now().toString() + Math.floor(Math.random() * 1000).toString();
};

// Send travel details to backend API
const sendTravelDetailsRequest = async (userInput: string) => {
  try {
    isLoading.value = true;

    // Create conversation history from existing messages
    const conversationHistory = messages.value.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Send request to backend
    const response = await axios.post(`${API_URL}/api/travel-details`, {
      user_input: userInput,
      conversation_history: conversationHistory,
    });

    const responseData = response.data;

    // Store travel details if available
    if (responseData.complete && responseData.travel_details) {
      travelDetails.value = responseData.travel_details;
      showFlightSearch.value = true;
    }

    // Add the assistant's message with the formatted response
    messages.value.push({
      id: generateMessageId(),
      content: responseData.message,
      role: MessageRole.Assistant,
    });

    return responseData;
  } catch (error) {
    console.error("Error sending travel details:", error);
    messages.value.push({
      id: generateMessageId(),
      content: "Sorry, I encountered an error processing your travel plans. Please try again.",
      role: MessageRole.Assistant,
    });
    return null;
  } finally {
    isLoading.value = false;
  }
};

const handleInputEnter = async () => {
  if (!input.value.trim() || isLoading.value) return;

  const userMessage: Message = {
    id: generateMessageId(),
    content: input.value,
    role: MessageRole.User,
  };

  messages.value.push(userMessage);

  // Add loading message
  const loadingMessageId = generateMessageId();
  messages.value.push({
    id: loadingMessageId,
    content: "Thinking...",
    role: MessageRole.Assistant,
  });

  const userInput = input.value;
  input.value = "";

  // Send request to backend
  await sendTravelDetailsRequest(userInput);

  // Remove loading message
  messages.value = messages.value.filter((msg) => msg.id !== loadingMessageId);
};

// Handle flight URL when it's ready
const handleFlightUrlReady = (url: string) => {
  // You can add additional logic here if needed
  console.log("Flight URL ready:", url);
};

// Function to clear messages when the clear-chat-state event is triggered
const clearChatState = () => {
  messages.value = [];
  input.value = "";
  travelDetails.value = null;
  showFlightSearch.value = false;
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
          I'm here to help you in planning your experience. Tell me your travel plan and I'll give
          you flights and hotel suggestions.
        </p>
      </Welcome>
      <div v-else class="flex flex-col w-full h-full overflow-y-auto">
        <ChatInterface :messages="messages" />

        <!-- Flight Search Component (only shown when travel details are available) -->
        <FlightSearch
          v-if="showFlightSearch && travelDetails"
          :travelDetails="travelDetails"
          @flightUrlReady="handleFlightUrlReady"
        />
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
