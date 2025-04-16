<script setup lang="ts">
import { ref } from "vue";

interface TooltipProps {
  text: string;
  position?: "top" | "right" | "bottom" | "left";
  hidden?: boolean;
  maxWidth?: number;
}

const props = withDefaults(defineProps<TooltipProps>(), {
  position: "bottom",
  hidden: false,
});

const showTooltip = ref(false);
</script>

<template>
  <div
    class="relative inline-block cursor-pointer"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
    @focus="showTooltip = true"
    @blur="showTooltip = false"
    tabindex="0"
  >
    <slot />
    <div
      v-if="showTooltip && !props.hidden"
      :class="[
        'absolute z-50 bg-gray-300 text-black py-1 px-2.5 rounded text-xs font-light pointer-events-none break-words',
        props.maxWidth && `w-${props.maxWidth}`,
        props.position === 'top' &&
          'bottom-full left-1/2 -translate-x-1/2 mb-2 after:content-[\'\'] after:absolute after:top-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent',
        props.position === 'right' &&
          'left-full top-1/2 -translate-y-1/2 ml-2 after:content-[\'\'] after:absolute after:right-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent',
        props.position === 'bottom' &&
          'top-full left-1/2 -translate-x-1/2 mt-2 after:content-[\'\'] after:absolute after:bottom-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent',
        props.position === 'left' &&
          'right-full top-1/2 -translate-y-1/2 mr-2 after:content-[\'\'] after:absolute after:left-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent',
      ]"
    >
      {{ props.text }}
    </div>
  </div>
</template>
