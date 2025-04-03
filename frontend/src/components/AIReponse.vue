<script setup lang="ts">
import Button from "./Button.vue";
import Icon from "./Icon.vue";

const props = defineProps<{
  content: string;
}>();
</script>

<template>
  <div class="flex gap-4 w-full text-white">
    <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-blue">
      <Icon name="bot" />
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <div class="whitespace-pre-wrap break-words text-white font-sans">
        {{ props.content }}
      </div>
      <div class="flex items-center gap-1">
        <Button variant="icon" tooltip tooltipText="Regenerate">
          <Icon name="refresh" size="text-base" />
        </Button>
        <Button variant="icon" tooltip tooltipText="Copy">
          <Icon name="copy" size="text-base" />
        </Button>
      </div>
    </div>
  </div>
</template>
