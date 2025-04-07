import { ref, onUnmounted } from "vue";
import { TaskStatus, TaskType, type Message, MessageRole } from "@/types";
import { checkTaskStatus, getTravelSummary } from "@/services/api";
import { useTravelStore } from "@/stores/travel";
import { marked } from "marked";
import { useTaskStore } from "@/stores/tasks";
import { generateId } from "@/utils/id";
import { formatTaskType } from "@/utils/common";
import { useTravelSearch } from "@/composables/useTravelSearch";

export function useTasks(
  setLoading: (loading: boolean) => void,
  addMessage: (message: Omit<Message, "id"> & { id?: string }) => void,
  updateMessage: (id: string, data: Partial<Message>) => void
) {
  const travelStore = useTravelStore();
  const taskStore = useTaskStore();

  const pollInterval = ref<number | null>(null);

  // Update task message progress based on status
  const updateTaskMessageProgress = (taskType: TaskType) => {
    const { messageId, status } = taskStore.tasks[taskType];

    if (messageId) {
      updateMessage(messageId, {
        loading: status === TaskStatus.Processing || status === TaskStatus.Pending,
      });
    }
  };

  const startPolling = (taskType: TaskType) => {
    // Poll every 2 seconds
    pollInterval.value = setInterval(() => {
      monitorTaskStatus(taskType);
    }, 2000) as unknown as number;
  };

  const stopPolling = () => {
    console.log("Stop polling", pollInterval.value);
    if (pollInterval.value !== null) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
    }
  };

  const setTaskProcessing = (taskType: TaskType, taskId: string) => {
    const taskState = taskStore.tasks[taskType];
    if (taskState) {
      taskStore.updateTask(taskType, {
        id: taskId,
        status: TaskStatus.Processing,
      });
      updateTaskMessageProgress(taskType);
      startPolling(taskType);
    }
  };

  const handleTaskStatusChange = async (taskType: TaskType, status: TaskStatus, data?: any) => {
    if (status === TaskStatus.Failed) {
      addMessage({
        role: MessageRole.Task,
        content: `${formatTaskType(taskType)} failed. Please try again.`,
        taskType: taskType,
      });
      setLoading(false);
    } else if (status === TaskStatus.Completed) {
      if (taskType === TaskType.FlightSearch) {
        travelStore.setContext({ flight_results: data });
        const output = await marked.parse(data);
        addMessage({
          role: MessageRole.Task,
          content: "🛫 I got some flight options for you.",
          collapsable_content: output,
          taskType: TaskType.FlightSearch,
        });

        if (!taskStore.tasks[TaskType.FlightSearch].regenerate) {
          // Start hotel search
          await startHotelSearch();
        }
      }
      if (taskType === TaskType.HotelSearch) {
        travelStore.setContext({ hotel_results: data });
        const output = await marked.parse(data);
        addMessage({
          role: MessageRole.Task,
          content: "🏨 I got some hotel options for you.",
          collapsable_content: output,
          taskType: TaskType.HotelSearch,
        });

        if (!taskStore.tasks[TaskType.HotelSearch].regenerate) {
          // Get travel summary
          await initializeTravelSummary();
        }
      }
    }
  };

  const initializeTravelSummary = async () => {
    const loadingMessageId = generateId();
    addMessage({
      id: loadingMessageId,
      role: MessageRole.Info,
      content: "✨ Putting together your perfect trip...",
      loading: true,
    });

    try {
      const summary = await getTravelSummary(travelStore.context!);
      const output = await marked.parse(summary);

      updateMessage(loadingMessageId, {
        loading: false,
      });
      addMessage({
        role: MessageRole.Assistant,
        content: output,
        taskType: TaskType.TravelSummary,
      });
    } catch (e) {
      console.error("Error getting travel summary:", e);
      updateMessage(loadingMessageId, {
        loading: false,
      });
      addMessage({
        role: MessageRole.Task,
        content: "Failed to get travel summary. Please try again.",
        taskType: TaskType.TravelSummary,
      });
    }

    setLoading(false);
  };

  const monitorTaskStatus = async (taskType: TaskType) => {
    try {
      // Check status of active task
      const taskState = taskStore.tasks[taskType as TaskType];
      if (taskState.id) {
        const { status, data } = await checkTaskStatus(taskState.id);

        // Update task status if changed
        if (taskState.status !== status) {
          taskStore.updateTask(taskType as TaskType, { status });
          updateTaskMessageProgress(taskType as TaskType);

          if (status === TaskStatus.Completed || status === TaskStatus.Failed) {
            stopPolling();
          }

          // Handle specific task status changes
          await handleTaskStatusChange(taskType as TaskType, status, data);
        }
      }
    } catch (e) {
      console.error("Error checking task status:", e);
      addMessage({
        role: MessageRole.Info,
        content: "An error occurred. Please try again.",
      });
      stopPolling();
    }
  };

  const initializeTask = (taskType: TaskType, message: Message, regenerate?: boolean) => {
    // Store task message ID and set initial progress
    taskStore.addTask({
      status: TaskStatus.Processing,
      type: taskType,
      messageId: message.id,
      regenerate: regenerate,
    });

    addMessage(message);
    return message.id;
  };

  // Initialize travel search after functions are defined
  const { startHotelSearch } = useTravelSearch(addMessage, setTaskProcessing, initializeTask);

  // Clean up polling when component is unmounted
  onUnmounted(() => {
    stopPolling();
  });

  return {
    startPolling,
    stopPolling,
    setTaskProcessing,
    initializeTask,
    initializeTravelSummary,
  };
}
