<script setup lang="ts">
import { twMerge } from "tailwind-merge";
import { computed, ref } from "vue";

interface ButtonProps {
  variant: "primary" | "secondary" | "icon" | "ghost";
  tooltip?: boolean;
  tooltipPosition?: "top" | "right" | "bottom" | "left";
  tooltipText?: string;
  class?: string;
}

const props = withDefaults(defineProps<ButtonProps>(), {
  tooltip: false,
  tooltipPosition: "bottom",
  tooltipText: "",
  class: "",
});

const showTooltip = ref(false);

const getVariantClasses = () => {
  switch (props.variant) {
    case "primary":
      return "bg-yellow-dark border-yellow-light text-white";
    case "secondary":
      return "bg-dark-400 text-gray-500 border-transparent";
    case "icon":
      return "w-8 h-8 flex items-center justify-center bg-transparent text-gray-500 border-none hover:text-gray-300 hover:bg-dark-200";
    case "ghost":
      return " p-0 bg-transparent text-gray-500 border-none hover:text-gray-300";
  }
};
const buttonClasses = computed(() => {
  const defaultClasses =
    " relative px-4 py-2 border text-sm font-semibold rounded-full cursor-pointer";
  return twMerge(defaultClasses, getVariantClasses(), props.class);
});
</script>

<template>
  <button :class="buttonClasses" @mouseenter="showTooltip = true" @mouseleave="showTooltip = false">
    <slot></slot>
    <div
      v-if="props.tooltip && showTooltip"
      class="absolute z-50 bg-gray-300 text-black py-1 px-2.5 rounded text-xs font-light whitespace-nowrap pointer-events-none"
      :class="[
        props.tooltipPosition === 'top' &&
          'bottom-full left-1/2 -translate-x-1/2 mb-2 after:content-[\'\'] after:absolute after:top-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-t-black/80',
        props.tooltipPosition === 'right' &&
          'left-full top-1/2 -translate-y-1/2 ml-2 after:content-[\'\'] after:absolute after:right-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-r-black/80',
        props.tooltipPosition === 'bottom' &&
          'top-full left-1/2 -translate-x-1/2 mt-2 after:content-[\'\'] after:absolute after:bottom-full after:left-1/2 after:-translate-x-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-b-black/80',
        props.tooltipPosition === 'left' &&
          'right-full top-1/2 -translate-y-1/2 mr-2 after:content-[\'\'] after:absolute after:left-full after:top-1/2 after:-translate-y-1/2 after:border-[5px] after:border-solid after:border-transparent after:border-l-black/80',
      ]"
    >
      {{ props.tooltipText }}
    </div>
  </button>
</template>
