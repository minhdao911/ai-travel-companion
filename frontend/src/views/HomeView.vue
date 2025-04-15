<script setup lang="ts">
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import { Tabs } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";
import { useTravelPlanner } from "@/composables/useTravelPlanner";

const { input, messages, isLoading, currentTaskId, handleInputEnter, onRegenerate } =
  useTravelPlanner();
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
        <ChatInterface :messages="messages" :isLoading="isLoading" :onRegenerate="onRegenerate" />
      </div>
      <TextInput
        :placeholder="'Where would you like to go?'"
        :activeTab="Tabs.FlightsAndHotels"
        v-model="input"
        :onEnter="handleInputEnter"
        :disabled="isLoading || !!currentTaskId"
      />
    </div>
  </Container>
</template>
