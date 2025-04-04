<script setup lang="ts">
import { ref, onUnmounted, defineEmits } from "vue";
import Button from "./Button.vue";
import axios from "axios";
import { type TravelDetails, TaskStatus } from "@/types";

const API_URL = import.meta.env.VITE_API_URL;

// Props to receive travel details data
const props = defineProps<{
  travelDetails: TravelDetails;
}>();

const emit = defineEmits(["flightUrlReady"]);

// State variables
const isSearching = ref(false);
const progress = ref(0);
const statusMessage = ref("");
const taskId = ref("");
const flightUrl = ref("");
const error = ref("");

// Poll for task status updates
const pollInterval = ref<number | null>(null);

const startFlightSearch = async () => {
  try {
    error.value = "";
    isSearching.value = true;
    progress.value = 10;
    statusMessage.value = "Finding available flights for your dates...";

    // Call the flight search API
    const response = await axios.post(`${API_URL}/api/search-flights`, {
      origin_city_name: props.travelDetails.origin_city_name,
      destination_city_name: props.travelDetails.destination_city_name,
      start_date: props.travelDetails.start_date,
      end_date: props.travelDetails.end_date,
      num_guests: props.travelDetails.num_guests,
    });

    // Store the task ID
    taskId.value = response.data.task_id;

    // Start polling for status updates
    startPolling();
  } catch (e) {
    console.error("Error starting flight search:", e);
    error.value = "Failed to start flight search. Please try again.";
    isSearching.value = false;
  }
};

const startPolling = () => {
  // Poll every 2 seconds
  pollInterval.value = setInterval(checkTaskStatus, 2000) as unknown as number;
};

const checkTaskStatus = async () => {
  try {
    if (!taskId.value) return;

    const response = await axios.get(`${API_URL}/api/task-status/${taskId.value}`);
    const { status, data, error: taskError } = response.data;

    // Update progress based on status
    if (status === TaskStatus.Pending) {
      progress.value = 30;
    } else if (status === TaskStatus.Processing) {
      progress.value = 60;
    } else if (status === TaskStatus.Completed) {
      progress.value = 100;
      statusMessage.value = "Flight search completed!";
      stopPolling();

      // Store the flight URL
      if (data && data.url) {
        flightUrl.value = data.url;
        emit("flightUrlReady", data.url);
      }
    } else if (status === TaskStatus.Failed) {
      stopPolling();
      error.value = taskError || "Flight search failed. Please try again.";
      isSearching.value = false;
    }
  } catch (e) {
    console.error("Error checking task status:", e);
    stopPolling();
    error.value = "Failed to check search status. Please try again.";
    isSearching.value = false;
  }
};

const stopPolling = () => {
  if (pollInterval.value !== null) {
    clearInterval(pollInterval.value);
    pollInterval.value = null;
  }
};

const openFlightResults = () => {
  if (flightUrl.value) {
    window.open(flightUrl.value, "_blank");
  }
};

// Clean up polling on component unmount
onUnmounted(() => {
  stopPolling();
});
</script>

<template>
  <div class="w-full mt-4 rounded-lg border border-gray-200 p-4 bg-white">
    <h3 class="text-lg font-semibold mb-2">Flight Search</h3>

    <div v-if="!isSearching && !flightUrl">
      <p class="text-sm text-gray-600 mb-4">
        Ready to search for flights based on your travel details.
      </p>
      <Button @click="startFlightSearch" variant="primary"> Search Flights </Button>
    </div>

    <div v-if="isSearching" class="my-4">
      <p class="text-sm text-gray-600 mb-2">{{ statusMessage }}</p>
      <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div
          class="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-in-out"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>

    <div v-if="flightUrl" class="my-4">
      <p class="text-sm text-gray-600 mb-4">
        Your flight search is complete! Click the button below to view available flights.
      </p>
      <Button @click="openFlightResults" variant="primary"> View Flights </Button>
    </div>

    <p v-if="error" class="text-sm text-red-600 mt-2">{{ error }}</p>
  </div>
</template>
