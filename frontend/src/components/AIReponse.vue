<script setup lang="ts">
import { ref } from "vue";
import Button from "./Button.vue";
import Icon from "./Icon.vue";
import { MessageRole, type Message } from "@/types";

const props = defineProps<{
  message: Message;
  isChatLoading: boolean;
}>();

const isCollapsableContentVisible = ref(false);

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

const toggleCollapsableContent = () => {
  isCollapsableContentVisible.value = !isCollapsableContentVisible.value;
};
</script>

<template>
  <div class="flex gap-4 w-full text-white">
    <div
      class="flex items-center justify-center w-8 h-8 rounded-lg shrink-0"
      :class="getIconStyle().color"
    >
      <Icon v-if="props.message.loading" name="spinner-dotted" class="animate-spin" />
      <Icon v-else :name="getIconStyle().icon" />
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <pre class="whitespace-pre-wrap break-words text-white font-sans">{{
        props.message.content
      }}</pre>

      <!-- Collapsable content -->
      <div v-if="props.message.collapsable_content" class="w-full">
        <Button
          variant="ghost"
          size="sm"
          @click="toggleCollapsableContent"
          class="flex items-center gap-2 mb-3"
        >
          <Icon :name="isCollapsableContentVisible ? 'angle-up' : 'angle-down'" size="text-sm" />
          <p>{{ isCollapsableContentVisible ? "Show less details" : "Show more details" }}</p>
        </Button>

        <pre
          v-if="isCollapsableContentVisible"
          class="whitespace-pre-wrap break-words text-white font-sans collapsable-content"
          >{{ props.message.collapsable_content }}</pre
        >
      </div>
    </div>
  </div>
</template>

<style scoped>
.collapsable-content {
  border-left: 2px solid #2f3245;
  padding-left: 16px;
  margin-left: 6px;
}
</style>
