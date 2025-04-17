<script setup lang="ts">
import { useTextareaAutosize } from "@vueuse/core";
import { computed, ref, watch, onMounted, nextTick } from "vue";

const textareaRef = ref<HTMLTextAreaElement | null>(null);

const props = defineProps<{
  placeholder: string;
  modelValue: string;
  disabled?: boolean;
  onEnter: () => void;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const focus = () => {
  if (textareaRef.value) {
    textareaRef.value.focus();
  }
};

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

// Focus the textarea when not disabled
watch(
  () => props.disabled,
  (isDisabled) => {
    if (!isDisabled) {
      nextTick(() => {
        focus();
      });
    }
  }
);

// Ensure proper initial focus state when component is mounted
onMounted(() => {
  if (!props.disabled) {
    nextTick(() => {
      focus();
    });
  }
});

const handleEnter = (event: KeyboardEvent) => {
  // Let Shift+Enter behavior happen naturally
  if (!event.shiftKey) {
    event.preventDefault();
    props.onEnter();
  }
};
</script>

<template>
  <div class="relative flex flex-col gap-6 bg-dark-500 border-dark-200 border rounded-[1rem] p-4">
    <textarea
      ref="textareaRef"
      v-model="inputValue"
      class="w-full border-none resize-none text-white placeholder-gray-500 focus:outline-none max-h-[10rem] hidden-scrollbar"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      rows="3"
      @keydown.enter="handleEnter"
    />
    <div class="absolute bottom-4 right-4 flex justify-between items-end">
      <p class="text-gray-500 text-sm">Enter to submit ⏎</p>
    </div>
  </div>
</template>
