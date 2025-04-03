<script setup lang="ts">
import { ref } from "vue";
import Container from "@/components/Container.vue";
import TextInput from "@/components/TextInput.vue";
import { Tabs, type Message } from "@/types";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";

const messages = ref<Message[]>([
  {
    id: "1",
    content: "I plan to go to Paris on the 1st of May",
    role: "user",
  },
  {
    id: "2",
    content: `I'm here to help you in planning your experience. Tell me your travel plan and I’ll give you flights and hotel suggestions.
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer tincidunt ipsum sem, in interdum turpis tincidunt ut. Fusce vel imperdiet massa. Curabitur volutpat metus sed lacinia feugiat. Nullam lacinia eget tortor sit amet vestibulum. Curabitur interdum massa at urna facilisis pellentesque. Vestibulum finibus nisl pellentesque elementum congue. Etiam at risus tempus dolor elementum aliquet. Integer egestas volutpat turpis nec tristique. Nunc arcu arcu, pharetra at ornare sed, imperdiet eget purus. Donec interdum in lorem luctus vestibulum. Etiam odio odio, iaculis dignissim suscipit at, euismod et enim. Morbi ac dignissim eros, sit amet malesuada elit. Cras fermentum lorem nec lectus sagittis auctor. Integer condimentum sed nisl ac porta.`,
    role: "assistant",
  },
]);

const input = ref("");

const handleInputEnter = () => {
  messages.value.push({
    id: "1",
    content: input.value,
    role: "user",
  });
  input.value = "";
};
</script>

<template>
  <main class="flex flex-col h-screen w-screen">
    <Container>
      <div class="flex flex-col justify-between w-full h-full">
        <Welcome v-if="messages.length === 0">
          <p class="text-gray-500 max-w-xl text-center">
            I’m here to help you in planning your experience. Tell me your travel plan and I’ll give
            you flights and hotel suggestions.
          </p>
        </Welcome>
        <ChatInterface v-else :messages="messages" />
        <TextInput
          placeholder="Where would you like to go?"
          :activeTab="Tabs.FlightsAndHotels"
          v-model="input"
          :onEnter="handleInputEnter"
        />
      </div>
    </Container>
  </main>
</template>
