<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";
import Button from "./Button.vue";
import Icon from "./Icon.vue";
import router from "@/router";
import { useAgentChatStore, useAssistantChatStore } from "@/stores/chat";

const agentChatStore = useAgentChatStore();
const assistantChatStore = useAssistantChatStore();

const links = [
  {
    name: "Flights and Hotels",
    icon: "flight",
    href: "/",
  },
  {
    name: "Assistant",
    icon: "chat",
    href: "/assistant",
  },
];

const isActiveLink = (path: string) => {
  const route = useRoute();
  return route.path === path;
};

const handleNewChat = () => {
  // Navigate to home page
  router.push("/");

  // Clear the chat state
  agentChatStore.resetChat();
  assistantChatStore.resetChat();
};
</script>

<template>
  <nav class="flex flex-col gap-6 p-4 min-w-64 h-full text-white">
    <Button variant="primary" @click="handleNewChat">New Chat</Button>
    <div class="flex flex-col gap-2.5 w-full">
      <p class="font-medium">Features</p>
      <RouterLink
        v-for="link in links"
        :key="link.name"
        :to="link.href"
        class="flex items-center gap-2 p-2 px-4 rounded-lg"
        :class="{
          'text-blue bg-dark-400': isActiveLink(link.href),
          'text-gray-500 hover:text-blue hover:bg-dark-400': !isActiveLink(link.href),
        }"
      >
        <Icon :name="link.icon" size="text-base" />
        <p>{{ link.name }}</p>
      </RouterLink>
    </div>
  </nav>
</template>
