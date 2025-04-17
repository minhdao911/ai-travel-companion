<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";
import Button from "./Button.vue";
import router from "@/router";
import { useChatStore } from "@/stores/chat";
import { v4 as uuidv4 } from "uuid";
import Tooltip from "./Tooltip.vue";

const chatStore = useChatStore();

const isActiveLink = (path: string) => {
  const route = useRoute();
  return route.path === path;
};

const handleNewChat = () => {
  const id = uuidv4();
  router.push(`/chat/${id}`);
  chatStore.addChat(id);
};
</script>

<template>
  <nav class="flex flex-col gap-6 p-4 w-68 h-full text-white flex-shrink-0">
    <Button variant="primary" @click="handleNewChat">New Chat</Button>
    <div class="flex flex-col gap-2.5 w-full">
      <p class="text-sm font-medium">History</p>
      <Tooltip
        v-if="chatStore.chats.length > 0"
        v-for="chat in chatStore.chats"
        :key="chat.id"
        :text="chat.title"
        position="bottom"
        :hidden="chat.title.length <= 25"
        :maxWidth="64"
      >
        <RouterLink
          :to="`/chat/${chat.id}`"
          class="relative flex items-center gap-2 p-2 px-4 rounded-lg group"
          :class="{
            'text-blue bg-dark-400': isActiveLink(`/chat/${chat.id}`),
            'text-gray-500 hover:text-blue hover:bg-dark-400': !isActiveLink(`/chat/${chat.id}`),
          }"
        >
          <p class="truncate">{{ chat.title }}</p>
        </RouterLink>
      </Tooltip>
      <p v-else class="text-sm text-gray-500 italic">Empty :((, create new chat to start</p>
    </div>
  </nav>
</template>
