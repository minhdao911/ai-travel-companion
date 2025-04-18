<script setup lang="ts">
import { twMerge } from "tailwind-merge";
import { computed, ref } from "vue";

interface ButtonProps {
  variant: "primary" | "secondary" | "icon" | "ghost";
  tooltip?: boolean;
  tooltipPosition?: "top" | "right" | "bottom" | "left";
  tooltipText?: string;
  class?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<ButtonProps>(), {
  tooltip: false,
  tooltipPosition: "bottom",
  tooltipText: "",
  class: "",
  disabled: false,
});

const showTooltip = ref(false);

const getVariantClasses = () => {
  switch (props.variant) {
    case "primary":
      return "bg-yellow-dark border-yellow-light text-white";
    case "secondary":
      return "bg-dark-400 text-blue border-dark-200";
    case "icon":
      return "w-8 h-8 flex items-center justify-center bg-transparent text-gray-500 border-none hover:text-gray-300 hover:bg-dark-200 disabled:hover:text-gray-500 disabled:hover:bg-transparent";
    case "ghost":
      return " p-0 bg-transparent text-gray-500 border-none hover:text-gray-300";
  }
};
const buttonClasses = computed(() => {
  const defaultClasses =
    "relative px-4 py-2 border text-sm font-semibold rounded-lg cursor-pointer";
  return twMerge(defaultClasses, getVariantClasses(), props.class);
});
</script>

<template>
  <button
    :class="buttonClasses"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
    :disabled="props.disabled"
  >
    <slot></slot>
    <div
      v-if="!props.disabled && props.tooltip && showTooltip"
      class="absolute z-50 bg-gray-300 text-black py-1 px-2.5 rounded text-xs font-light whitespace-nowrap pointer-events-none"
      :class="[
        props.tooltipPosition === 'top' && 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        props.tooltipPosition === 'right' && 'left-full top-1/2 -translate-y-1/2 ml-2',
        props.tooltipPosition === 'bottom' && 'top-full left-1/2 -translate-x-1/2 mt-2',
        props.tooltipPosition === 'left' && 'right-full top-1/2 -translate-y-1/2 mr-2',
      ]"
    >
      {{ props.tooltipText }}
    </div>
  </button>
</template>
