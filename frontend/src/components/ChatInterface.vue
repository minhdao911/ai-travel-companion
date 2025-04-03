<script setup lang="ts">
import ChatBubble from "@/components/ChatBubble.vue";
import AIReponse from "@/components/AIReponse.vue";
import type { Message } from "@/types";

const props = defineProps<{
  messages: Message[];
}>();
</script>

<template>
  <div class="flex-1 flex flex-col gap-8">
    <template v-for="message in props.messages" :key="message.id">
      <!-- Use ChatBubble for user messages -->
      <ChatBubble v-if="message.role === 'user'" :content="message.content" />

      <!-- Use normal div for assistant messages -->
      <AIReponse v-else class="w-full text-white" :content="message.content" />
    </template>
  </div>
</template>
