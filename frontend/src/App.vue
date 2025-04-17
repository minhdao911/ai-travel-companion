<script setup lang="ts">
import { RouterView } from "vue-router";
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="flex p-4 h-screen w-screen gap-4">
    <NavBar />
    <RouterView />
  </div>
</template>
