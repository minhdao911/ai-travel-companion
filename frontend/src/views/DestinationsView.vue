<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6 text-blue-600">Travel Destinations</h1>

    <div v-if="loading" class="text-center py-8">
      <p class="text-lg text-gray-600">Loading destinations...</p>
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      <p>{{ error }}</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="destination in destinations"
        :key="destination.id"
        class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
      >
        <div class="p-6">
          <h2 class="text-xl font-bold text-gray-800">{{ destination.name }}</h2>
          <p class="text-sm text-gray-600 mb-2">{{ destination.country }}</p>
          <p class="text-gray-700">{{ destination.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

interface Destination {
  id: number;
  name: string;
  country: string;
  description: string;
}

const destinations = ref<Destination[]>([]);
const loading = ref(true);
const error = ref("");

const fetchDestinations = async () => {
  try {
    loading.value = true;
    const response = await fetch("http://localhost:8000/api/destinations");

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    destinations.value = data.destinations;
  } catch (err) {
    console.error("Error fetching destinations:", err);
    error.value = "Failed to load destinations. Please try again later.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDestinations();
});
</script>
