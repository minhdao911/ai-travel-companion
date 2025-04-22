<script setup lang="ts">
const props = defineProps<{
  isLoading: boolean;
  text?: string;
}>();
</script>

<template>
  <div class="loader" :class="{ loaded: !props.isLoading }">
    <div class="spinner"></div>
    <p>{{ props.text }}</p>
  </div>
</template>

<style scoped>
.loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: var(--color-dark-500);
  z-index: 9999;
  transition: opacity 0.5s, visibility 0.5s;
}

.loader p {
  margin-top: 1rem;
  color: white;
  font-size: 1.2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  border-top-color: var(--color-blue);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loaded.loader {
  opacity: 0;
  visibility: hidden;
}
</style>
