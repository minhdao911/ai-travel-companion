<script setup lang="ts">
import { useTextareaAutosize } from "@vueuse/core";
import { computed, ref, watch, onMounted, nextTick } from "vue";
import Icon from "@/components/Icon.vue";
import { type AIModel } from "@/types";

const textareaRef = ref<HTMLTextAreaElement | null>(null);
const isDropdownOpen = ref(false);

const props = defineProps<{
  placeholder: string;
  modelValue: string;
  disabled?: boolean;
  onEnter: () => void;
  availableModels?: AIModel[];
  selectedModel?: AIModel;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
  "update:selectedModel": [value: AIModel];
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

const selectModel = (model: AIModel) => {
  emit("update:selectedModel", model);
  isDropdownOpen.value = false;
};

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

// Close dropdown when clicking outside
const closeDropdown = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest(".model-selector")) {
    isDropdownOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", closeDropdown);
});
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

    <div class="absolute bottom-4 left-4 right-4 flex justify-between items-end">
      <!-- Model selector dropdown -->
      <div
        v-if="props.availableModels && props.availableModels.length > 0"
        class="model-selector relative"
      >
        <button
          @click="toggleDropdown"
          class="text-sm text-gray-400 hover:text-gray-300 flex items-center gap-1 px-2 py-1 rounded-md hover:bg-dark-400"
        >
          <p>
            {{
              props.availableModels.find((m) => m.id === props.selectedModel?.id)?.name ||
              "Select model"
            }}
          </p>
          <Icon name="angle-down" class="w-3 h-3" />
        </button>

        <div
          v-if="isDropdownOpen"
          class="absolute flex flex-col gap-1 bottom-full left-0 mb-1 bg-dark-400 rounded-md shadow-lg z-10 w-max p-1"
        >
          <button
            v-for="model in props.availableModels"
            :key="model.id"
            @click="selectModel(model)"
            class="block w-full text-left px-4 py-2 text-sm text-gray-400 hover:bg-dark-500 rounded"
            :class="{ 'bg-dark-500 text-white': model.id === props.selectedModel?.id }"
          >
            {{ model.name }}
          </button>
        </div>
      </div>

      <p class="text-gray-500 text-sm">Enter to submit ⏎</p>
    </div>
  </div>
</template>
