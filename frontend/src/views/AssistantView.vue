<script setup lang="ts">
import { ref } from "vue";
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import Card from "@/components/Card.vue";
import { MessageRole, Tabs, type Message } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";

const messages = ref<Message[]>([]);
const input = ref("");
const textInputRef = ref<InstanceType<typeof TextInput> | null>(null);

const defaultPrompts = [
  "Create a 7-day itinerary for my trip",
  "What are the must-see attractions?",
  "What are the most popular restaurants in ...?",
  "How do I get from airport to my hotel?",
];

const handleCardClick = (prompt: string) => {
  input.value = prompt;
  if (textInputRef.value) {
    textInputRef.value.focus();
  }
};

const handleInputEnter = () => {
  messages.value.push({
    id: "1",
    content: input.value,
    role: MessageRole.User,
  });
  input.value = "";
};

const handleRegenerate = (messageId: string) => {
  console.log("Regenerating", messageId);
};
</script>

<template>
  <Container>
    <div class="flex flex-col justify-between w-full h-full">
      <Welcome v-if="messages.length === 0">
        <div class="flex flex-col gap-2.5 w-xl">
          <p class="text-gray-500">
            Learn about local restaurants, attractions and travel tips. I can search the web for
            up-to-date information about your destinations.
          </p>
          <p class="text-gray-500">Use the prompts below or use your own to get started.</p>
          <div class="grid grid-cols-2 gap-2.5">
            <Card
              v-for="prompt in defaultPrompts"
              :key="prompt"
              :onClick="() => handleCardClick(prompt)"
            >
              <p class="text-white text-sm">{{ prompt }}</p>
            </Card>
          </div>
        </div>
      </Welcome>
      <ChatInterface
        v-else
        :messages="messages"
        :isLoading="false"
        :onRegenerate="handleRegenerate"
      />
      <TextInput
        v-model="input"
        placeholder="Write a message..."
        :activeTab="Tabs.Assistant"
        :onEnter="handleInputEnter"
        ref="textInputRef"
      />
    </div>
  </Container>
</template>
