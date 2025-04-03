<script setup lang="ts">
const props = defineProps<{
  onClick: () => void;
}>();
</script>

<template>
  <div class="border-dark-200 border rounded-xl p-2.5 cursor-pointer" @click="props.onClick">
    <slot></slot>
  </div>
</template>
