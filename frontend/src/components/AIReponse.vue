<script setup lang="ts">
import { ref } from "vue";
import Button from "./Button.vue";
import Icon from "./Icon.vue";
import { MessageRole, type Message } from "@/types";

const emit = defineEmits<{
  (e: "regenerate", messageId: string): void;
}>();

const props = defineProps<{
  message: Message;
  isChatLoading: boolean;
}>();

const isCopied = ref(false);

const getIconStyle = () => {
  switch (props.message.role) {
    case MessageRole.Info:
      return {
        icon: "wrench",
        color: "bg-dark-200",
      };
    case MessageRole.Task:
      return {
        icon: "bolt",
        color: "bg-yellow-light",
      };
    default:
      return {
        icon: "bot",
        color: "bg-blue",
      };
  }
};

const handleCopy = () => {
  navigator.clipboard.writeText(props.message.content);
  isCopied.value = true;
  setTimeout(() => {
    isCopied.value = false;
  }, 1000);
};

const handleRegenerate = () => {
  emit("regenerate", props.message.id);
};
</script>

<template>
  <div class="flex gap-4 w-full text-white">
    <div class="flex items-center justify-center w-8 h-8 rounded-lg" :class="getIconStyle().color">
      <Icon v-if="props.message.loading" name="spinner-dotted" class="animate-spin" />
      <Icon v-else :name="getIconStyle().icon" />
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <div
        class="flex flex-col gap-2 text-white task-response"
        :class="{ 'whitespace-pre-wrap': props.message.role === MessageRole.Assistant }"
        v-html="props.message.content"
      ></div>
      <div
        v-if="
          !props.message.loading && !props.isChatLoading && props.message.role !== MessageRole.Info
        "
        class="flex items-center gap-1"
      >
        <Button variant="icon" tooltip tooltipText="Regenerate" @click="handleRegenerate">
          <Icon name="refresh" size="text-base" />
        </Button>
        <Button
          variant="icon"
          tooltip
          :tooltipText="isCopied ? 'Copied' : 'Copy'"
          @click="handleCopy"
        >
          <Icon name="copy" size="text-base" />
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-response :deep(strong) {
  font-weight: 600;
}

.task-response :deep(ul) {
  list-style-type: disc;
  margin-left: 1rem;
}

.task-response :deep(hr) {
  margin: 1rem 0;
  color: var(--color-gray-500);
}
</style>
