<script setup lang="ts">
import { ref, watchEffect, defineProps, markRaw } from "vue";

const props = defineProps<{
  name: string;
  size?: string;
}>();

const iconComponent = ref(null);

watchEffect(async () => {
  try {
    // Dynamic import of SVG as a component
    const module = await import(`@/assets/${props.name}.svg?component`);
    iconComponent.value = markRaw(module.default);
  } catch (error) {
    iconComponent.value = null;
  }
});
</script>

<template>
  <component :is="iconComponent" v-if="iconComponent" class="icon" />
  <i v-else :class="['pi', `pi-${props.name || 'question-circle'}`, props.size]"></i>
</template>

<style scoped>
.icon {
  display: inline-block;
  vertical-align: middle;
  width: v-bind("props.size || 'auto'");
  height: v-bind("props.size || 'auto'");
}
</style>
