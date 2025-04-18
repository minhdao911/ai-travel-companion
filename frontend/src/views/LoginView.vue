<script setup lang="ts">
import Container from "@/components/Container.vue";
import Button from "@/components/Button.vue";
import { ref } from "vue";
import { verifyAdmin } from "@/services/api";
import { useRouter } from "vue-router";
import useAuthStore from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");

const handleSubmit = async () => {
  const isAdmin = await authStore.verifyAdmin(username.value, password.value);
  if (isAdmin) {
    router.push("/chat");
  } else {
    alert("Incorrect username or password");
  }
};
</script>

<template>
  <Container>
    <div class="flex flex-col items-center justify-center h-full">
      <form class="flex flex-col items-center justify-center gap-3" @submit.prevent="handleSubmit">
        <input
          class="w-64 bg-dark-500 border-dark-200 border rounded-[1rem] p-4 focus:outline-none text-white placeholder-gray-500"
          type="text"
          placeholder="Username"
          v-model="username"
        />
        <input
          class="w-64 bg-dark-500 border-dark-200 border rounded-[1rem] p-4 focus:outline-none text-white placeholder-gray-500"
          type="password"
          placeholder="Password"
          v-model="password"
        />
        <Button variant="primary" class="w-full" type="submit">Login</Button>
      </form>
    </div>
  </Container>
</template>
