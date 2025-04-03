<script setup lang="ts">
import Button from "@/components/Button.vue";
import router from "@/router";
import { useTextareaAutosize } from "@vueuse/core";
import { Tabs } from "@/types";
import { computed, ref, watch } from "vue";

const textareaRef = ref<HTMLTextAreaElement | null>(null);

const props = defineProps<{
  placeholder: string;
  activeTab: Tabs;
  modelValue: string;
  onEnter: () => void;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

// Define methods to expose to parent components
const focus = () => {
  if (textareaRef.value) {
    textareaRef.value.focus();
  }
};

// Expose the focus method to parent components
defineExpose({
  focus,
});

// Create a computed property for two-way binding
const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

// Setup textarea autosize after inputValue is defined
const { textarea } = useTextareaAutosize({ input: inputValue, styleProp: "minHeight" });

// Make sure our DOM ref and the composable ref are synchronized
watch(
  () => textareaRef.value,
  (el) => {
    if (el) textarea.value = el;
  },
  { immediate: true }
);

const handleFlightsAndHotelsClick = () => {
  router.push("/");
};

const handleAssistantClick = () => {
  router.push("/assistant");
};

const handleEnter = (event: KeyboardEvent) => {
  if (!event.shiftKey) {
    event.preventDefault();
    props.onEnter();
  }
  // Let Shift+Enter behavior happen naturally
};
</script>

<template>
  <div class="relative flex flex-col gap-6 bg-dark-500 border-dark-200 border rounded-[1rem] p-4">
    <textarea
      ref="textareaRef"
      v-model="inputValue"
      class="w-full border-none resize-none text-white placeholder-gray-500 focus:outline-none max-h-[10rem]"
      :placeholder="props.placeholder"
      rows="3"
      @keydown.enter="handleEnter"
    />
    <div class="absolute bottom-4 right-4 flex justify-between items-end">
      <p class="text-gray-500 text-sm">Enter to submit ⏎</p>
    </div>
  </div>
</template>
