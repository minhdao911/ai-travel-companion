<script setup lang="ts">
import TextInput from "@/components/TextInput.vue";
import Welcome from "@/components/Welcome.vue";
import ChatInterface from "@/components/ChatInterface.vue";
import Container from "@/components/Container.vue";
import NavBar from "@/components/NavBar.vue";
import { useChat } from "@/composables/useChat";
import { useRoute, useRouter } from "vue-router";
import { v4 as uuidv4 } from "uuid";
import { useChatStore } from "@/stores/chat";
import { ref, watch } from "vue";
import { getChatTitle } from "@/services/api";

const route = useRoute();
const router = useRouter();

const chatStore = useChatStore();

const chatId = ref<string>("");

const { input, messages, isLoading, handleInputEnter } = useChat(chatId);

watch(
  () => route.params.id as string,
  (id) => {
    if (id === "new") {
      const newUuid = uuidv4();
      chatStore.addChat(newUuid);
      router.replace(`/chat/${newUuid}`);
    } else if (id) {
      chatId.value = id;
      if (!chatStore.getChat(id)) {
        chatStore.addChat(id);
      }
    }
  },
  { immediate: true }
);

// Watch for changes in messages to detect when the first message is added
watch(
  () => messages.value.length,
  async (newLength) => {
    if (newLength === 2) {
      const title = await getChatTitle(messages.value[0].content);
      chatStore.updateChat(chatId.value, { title });
    }
  },
  { immediate: true }
);
</script>

<template>
  <NavBar />
  <Container>
    <div class="flex flex-col justify-between w-full h-full">
      <Welcome v-if="messages.length === 0">
        <p class="text-gray-500 max-w-xl text-center">
          I'm here to help you in planning your experience. From finding the best flight and hotel
          options to answering questions about local restaurants, attractions, travel tips, and
          other travel-related information.
        </p>
      </Welcome>
      <div v-else class="flex flex-col w-full h-full overflow-y-auto">
        <ChatInterface :messages="messages" :isLoading="isLoading" />
      </div>
      <TextInput
        placeholder="Ask me anything about travel"
        v-model="input"
        :onEnter="handleInputEnter"
        :disabled="isLoading"
      />
    </div>
  </Container>
</template>
