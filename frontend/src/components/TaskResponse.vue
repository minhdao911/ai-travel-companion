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
      <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-yellow-500">
        <Icon v-if="isLoading" name="spinner-dotted" class="animate-spin" />
        <Icon v-else name="bolt" />
      </div>
      <div
        class="flex-1 whitespace-pre-wrap break-words text-white font-sans"
        v-html="formattedContent"
      ></div>
    </div>
  </div>
</template>
