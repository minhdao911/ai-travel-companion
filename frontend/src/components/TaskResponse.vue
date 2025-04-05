<script setup lang="ts">
import { ref } from "vue";
import Icon from "./Icon.vue";

const props = defineProps<{
  content: string;
  isLoading?: boolean;
}>();

const formattedContent = ref(props.content);
</script>
<template>
  <div class="flex flex-col gap-2 w-full text-white">
    <div class="flex gap-4 w-full">
      <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-yellow-light">
        <Icon v-if="isLoading" name="spinner-dotted" class="animate-spin" />
        <Icon v-else name="bolt" />
      </div>
      <div class="flex flex-col gap-2 text-white task-response" v-html="formattedContent"></div>
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
