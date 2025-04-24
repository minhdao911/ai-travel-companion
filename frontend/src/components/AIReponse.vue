<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import Button from "./Button.vue";
import Icon from "./Icon.vue";
import { MessageRole, type Message } from "@/types";
import { marked } from "marked";
import { createMarkdownRenderder } from "@/utils/common";

const props = defineProps<{
  message: Message;
  isChatLoading: boolean;
  isLastMessage: boolean;
}>();

const emit = defineEmits<{
  (e: "regenerate", id: string): void;
}>();

// --- Marked Renderer Setup ---
const renderer = createMarkdownRenderder();
const parseMarkdown = async (content: string): Promise<string> => {
  return await marked.parse(content || "", { renderer });
};

const isCollapsableContentVisible = ref(false);
const htmlContent = ref("");

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

onMounted(async () => {
  htmlContent.value = await parseMarkdown(props.message.content);
});

watch(
  () => props.message.content,
  async (newMessage) => {
    htmlContent.value = await parseMarkdown(newMessage);
  }
);

const toggleCollapsableContent = () => {
  isCollapsableContentVisible.value = !isCollapsableContentVisible.value;
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
      <Icon v-if="props.message.status === 'loading'" name="spinner-dotted" class="animate-spin" />
      <Icon v-else :name="getIconStyle().icon" />
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <div
        class="flex flex-col gap-2 w-fit font-sans text-white task-response"
        v-html="htmlContent"
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

        <pre
          v-if="isCollapsableContentVisible"
          class="whitespace-pre-wrap break-words text-white font-sans collapsable-content"
          >{{ props.message.collapsable_content }}</pre
        >
      </div>

      <div
        v-if="!props.isChatLoading && props.isLastMessage && props.message.status === 'error'"
        class="flex items-center gap-1"
      >
        <Button variant="icon" tooltip tooltipText="Regenerate" @click="handleRegenerate">
          <Icon name="refresh" size="text-base" />
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  margin-bottom: 6px;
}

.task-response :deep(ol) {
  list-style-type: decimal;
  margin-left: 1rem;
  margin-bottom: 6px;
}

.task-response :deep(hr) {
  margin: 1rem 0;
  color: var(--color-gray-500);
}

.task-response :deep(a) {
  text-decoration: underline;
}

.collapsable-content {
  border-left: 2px solid #2f3245;
  padding-left: 16px;
  margin-left: 6px;
}
</style>
