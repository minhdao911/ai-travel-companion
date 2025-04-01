<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-blue-600 text-white shadow-md">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="text-xl font-bold">AI Travel Companion</div>
        <div class="space-x-4">
          <RouterLink to="/" class="hover:text-blue-200 transition-colors">Home</RouterLink>
          <RouterLink to="/destinations" class="hover:text-blue-200 transition-colors"
            >Destinations</RouterLink
          >
        </div>
      </div>
    </nav>

    <main class="container mx-auto py-4">
      <RouterView />
    </main>
  </div>
</template>
