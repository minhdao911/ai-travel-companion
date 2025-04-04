<script setup lang="ts">
import ChatBubble from "@/components/ChatBubble.vue";
import AIReponse from "@/components/AIReponse.vue";
import TaskResponse from "@/components/TaskResponse.vue";
import type { Message } from "@/types";

const props = defineProps<{
  messages: Message[];
}>();
</script>

<template>
  <div class="flex-1 flex flex-col gap-8 py-8 overflow-y-auto hidden-scrollbar">
    <template v-for="message in props.messages" :key="message.id">
      <!-- Use ChatBubble for user messages -->
      <ChatBubble v-if="message.role === 'user'" :content="message.content" />

      <!-- Use AIReponse for assistant messages -->
      <AIReponse v-if="message.role === 'assistant'" :content="message.content" />

      <!-- Use TaskResponse for task messages -->
      <TaskResponse
        v-if="message.role === 'task'"
        :content="message.content"
        :isLoading="!message.completed"
      />
    </template>
  </div>
</template>
