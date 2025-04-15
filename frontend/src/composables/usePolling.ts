import { ref, onUnmounted, readonly } from "vue";

// Define a type for the poll function
type PollFunction<T> = (taskId: string) => Promise<T>;

// Define a type for the poll response handler
type ResponseHandler<T> = (response: T) => void;

// Define a type for the error handler
type ErrorHandler = (error: any) => void;

// Define options for the usePolling composable
interface UsePollingOptions<T> {
  pollFunction: PollFunction<T>;
  onSuccess: ResponseHandler<T>;
  onProcessing?: ResponseHandler<T>;
  onError: ErrorHandler;
  pollInterval?: number; // Interval in milliseconds
}

/**
 * Composable for polling an asynchronous task.
 *
 * @param options Configuration options for polling.
 * @returns Functions and reactive state for controlling and monitoring the polling process.
 */
export function usePolling<T>(options: UsePollingOptions<T>) {
  const {
    pollFunction,
    onSuccess,
    onProcessing,
    onError,
    pollInterval = 3000, // Default interval: 3 seconds
  } = options;

  const currentTaskId = ref<string | null>(null);
  const isPolling = ref(false);
  const pollIntervalId = ref<number | null>(null);

  const stopPolling = () => {
    if (pollIntervalId.value !== null) {
      clearInterval(pollIntervalId.value);
      pollIntervalId.value = null;
      isPolling.value = false;
      currentTaskId.value = null; // Clear task ID when stopping
      console.log("Polling stopped.");
    }
  };

  const startPolling = (taskId: string) => {
    stopPolling(); // Ensure any previous polling is stopped
    currentTaskId.value = taskId;
    isPolling.value = true;
    console.log(`Polling started for task ID: ${taskId}`);

    const poll = async () => {
      if (!currentTaskId.value) {
        stopPolling();
        return;
      }
      if (!isPolling.value) {
        console.log(`Polling flag is false for task ${taskId}. Stopping.`);
        stopPolling();
        return;
      }

      try {
        const response = await pollFunction(currentTaskId.value);

        // Check again if polling was stopped while waiting for the response
        if (!isPolling.value || currentTaskId.value !== taskId) {
          console.log(
            `Ignoring stale poll response for task ${taskId} as polling has stopped or task ID changed.`
          );
          return;
        }

        const status = (response as any).status;
        if (status === "COMPLETED") {
          onSuccess(response);
          stopPolling(); // Stop polling on completion
        } else if (status === "PROCESSING" || status === "PENDING") {
          if (onProcessing) {
            onProcessing(response);
          }
          // Continue polling for PROCESSING/PENDING
        } else if (status === "FAILED") {
          // Extract error message more robustly
          const errorMessage =
            (response as any).error ||
            (response as any).data?.error_message ||
            "Polling task failed";
          onError(errorMessage);
          stopPolling(); // Stop polling on failure
        } else {
          // Handle unexpected status or structure if necessary
          console.warn("Unexpected poll response status:", status, response);
          onError(`Unexpected poll response status: ${status}`);
          stopPolling();
        }
      } catch (error) {
        console.error("Error during polling:", error);
        onError(error); // Pass the error to the handler
        stopPolling(); // Stop polling on error
      }
    };

    // Run the first poll immediately, then set interval
    poll();
    pollIntervalId.value = setInterval(poll, pollInterval);
  };

  // Cleanup polling when the component is unmounted
  onUnmounted(() => {
    stopPolling();
  });

  return {
    startPolling,
    stopPolling,
    isPolling: readonly(isPolling),
    currentTaskId: readonly(currentTaskId),
  };
}
