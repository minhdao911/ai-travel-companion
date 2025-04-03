<script setup lang="ts">
import { ref } from "vue";
import Button from "./Button.vue";

const props = defineProps<{
  content: string;
}>();

const isCopied = ref(false);

const handleCopy = () => {
  navigator.clipboard.writeText(props.content);
  isCopied.value = true;
  setTimeout(() => {
    isCopied.value = false;
  }, 1000);
};
</script>

<template>
  <div class="group relative self-end max-w-xl bg-dark-200 rounded-[1rem] px-4 py-3">
    <pre class="whitespace-pre-wrap break-words text-white font-sans">{{ props.content }}</pre>
    <div
      class="absolute -bottom-6 left-0 right-0 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-200"
    >
      <Button variant="ghost" @click="handleCopy">
        <div class="flex items-center gap-1">
          <p class="font-normal text-sm">{{ isCopied ? "Copied" : "Copy" }}</p>
          <i class="pi pi-copy text-base"></i>
        </div>
      </Button>
    </div>
  </div>
</template>
