<script setup lang="ts">
import { ref } from "vue";
import Icon from "./Icon.vue";

interface IconTooltipProps {
  /**
   * The icon class (using a font icon library like Font Awesome, Material Icons, etc.)
   */
  icon: string;
  /**
   * The tooltip text
   */
  text: string;
  /**
   * Position of the tooltip (top, right, bottom, left)
   */
  position?: "top" | "right" | "bottom" | "left";
}

const props = withDefaults(defineProps<IconTooltipProps>(), {
  position: "bottom",
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
    <Icon :name="props.icon" />
    <div
      v-if="showTooltip"
      class="absolute z-50 bg-gray-300 text-black py-1 px-2.5 rounded text-xs font-light whitespace-nowrap pointer-events-none"
      :class="[
        props.position === 'top' &&
          'bottom-full left-1/2 -translate-x-1/2 mb-2 after:content-[\'\'] after:absolute after:top-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-t-black/80',
        props.position === 'right' &&
          'left-full top-1/2 -translate-y-1/2 ml-2 after:content-[\'\'] after:absolute after:right-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-r-black/80',
        props.position === 'bottom' &&
          'top-full left-1/2 -translate-x-1/2 mt-2 after:content-[\'\'] after:absolute after:bottom-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-b-black/80',
        props.position === 'left' &&
          'right-full top-1/2 -translate-y-1/2 mr-2 after:content-[\'\'] after:absolute after:left-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-l-black/80',
      ]"
    >
      {{ props.text }}
    </div>
  </div>
</template>
