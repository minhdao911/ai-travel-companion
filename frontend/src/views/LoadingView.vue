<script setup lang="ts">
import Loader from "@/components/Loader.vue";
import useAuthStore from "@/stores/auth";
import { onMounted } from "vue";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  console.log("Initial admin check...");
  await authStore.checkAdmin();
  console.log("Admin check complete");
  router.push({ name: "new-chat" });
});
</script>

<template>
  <Loader :isLoading="!authStore.adminChecked" text="Loading..." />
</template>
