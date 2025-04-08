<script setup lang="ts">
import { ref } from "vue";
import Button from "./Button.vue";
import Icon from "./Icon.vue";
import { MessageRole, TaskType, type Message } from "@/types";

const regeneratableTasks = [TaskType.FlightSearch, TaskType.HotelSearch, TaskType.TravelSummary];

const emit = defineEmits<{
  (e: "regenerate", messageId: string): void;
}>();

const props = defineProps<{
  message: Message;
  isChatLoading: boolean;
}>();

const isCopied = ref(false);
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
    <div
      class="flex items-center justify-center w-8 h-8 rounded-lg shrink-0"
      :class="getIconStyle().color"
    >
      <Icon v-if="props.message.loading" name="spinner-dotted" class="animate-spin" />
      <Icon v-else :name="getIconStyle().icon" />
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <div
        class="flex flex-col gap-2 w-fit text-white task-response"
        v-html="props.message.content"
      ></div>

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

        <div
          v-if="isCollapsableContentVisible"
          class="flex flex-col gap-2 w-fit text-gray-200 task-response collapsable-content"
          v-html="props.message.collapsable_content"
        ></div>
      </div>

      <div
        v-if="
          !props.message.loading &&
          !props.isChatLoading &&
          props.message.taskType &&
          regeneratableTasks.includes(props.message.taskType)
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
.task-response * {
  margin-bottom: 6px;
}

.task-response :deep(h1) {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 15px;
}

.task-response :deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.task-response :deep(h3) {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.task-response :deep(strong) {
  font-weight: 600;
  line-height: 1.75;
}

.task-response :deep(ul) {
  list-style-type: disc;
  margin-left: 1rem;
}

.task-response :deep(hr) {
  margin: 1rem 0;
  color: var(--color-gray-500);
}

.collapsable-content {
  border-left: 2px solid #2f3245;
  padding-left: 16px;
  margin-left: 6px;
}
</style>
