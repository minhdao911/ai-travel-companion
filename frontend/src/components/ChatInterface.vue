<script setup lang="ts">
import ChatBubble from "@/components/ChatBubble.vue";
import AIReponse from "@/components/AIReponse.vue";
import type { Message } from "@/types";

const props = defineProps<{
  messages: Message[];
  isLoading: boolean;
  onRegenerate: (messageId: string) => void;
}>();

const handleRegenerate = (messageId: string) => {
  props.onRegenerate(messageId);
};
</script>

<template>
  <div class="flex-1 flex flex-col gap-8 py-8 overflow-y-auto hidden-scrollbar">
    <template v-for="message in props.messages" :key="message.id">
      <!-- Use ChatBubble for user messages -->
      <ChatBubble v-if="message.role === 'user'" :content="message.content" />

      <!-- Use AIReponse for ai messages -->
      <AIReponse
        v-else
        :message="message"
        :isChatLoading="props.isLoading"
        @regenerate="handleRegenerate"
      />
    </template>
  </div>
</template>
